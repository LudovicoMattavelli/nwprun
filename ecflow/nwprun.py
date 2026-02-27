import ecflow
import os
# python 2/3 compatibility (in python2 raw_input)
try:
    input = raw_input
except NameError:
    pass

# from https://www.google.com/url?q=https://rosettacode.org/wiki/Range_expansion%23Python&sa=D&ust=1517307153586000&usg=AFQjCNHTzzU1Kk2XfryWWIoWwKTWNWItiw
def rangeexpand(txt):
    lst = []
    for r in txt.split(','):
        if '-' in r[1:]:
            r0, r1 = r[1:].split('-', 1)
            lst += range(int(r[0] + r0), int(r1) + 1)
        else:
            lst.append(int(r))
    return lst


def expr_or(expr, orexpr):
    if expr == "":
        return orexpr
    elif orexpr == "":
        return expr
    else:
        return expr+" || "+orexpr


def ask_confirm(msg=""):
    ans = input(msg+" (y/n)? ")
    return ans.startswith("y")


def daily_cron(step):
    if step > 60 or step < 0:
        return None
    time_series = ecflow.TimeSeries(ecflow.TimeSlot(0, 0),
                                    ecflow.TimeSlot(23, 60-step),
                                    ecflow.TimeSlot(0,step), False)
    cron = ecflow.Cron()
    cron.set_time_series(time_series)
    return cron


def cron_set_time(time):
    cron = ecflow.Cron()
    cron.set_time_series(time)
    return cron


# Merge the requested configuration with the library default.
class ModelConfig:
    def __init__(self, conf={}):
        self.conf = {"runlist": [],
                     "membrange": "0", "nofail": False, "modelname": "cosmo",
                     "gts": True, "lhn": True, "radarvol": False,
                     "preprocname": None, "getparentname": "get_parent",
                     "postprocrange": None, "postproctype": "async", 
                     "timer": None, "cronfreq": 10,
                     "startmethod": "check_run",
                     "starttime": "00:00", "epspostproclevel": 1}
        self.conf.update(conf) # update default with user data
        # special treatment for some fields
        self.conf['membrange'] = rangeexpand(self.conf['membrange'])
        if self.conf['postprocrange'] is None:
            self.conf['postprocrange'] = self.conf['membrange']
        else:
            self.conf['postprocrange'] = rangeexpand(self.conf['postprocrange'])
        if self.conf['modelname'] == "cosmo":
            self.conf['postprocname'] = "postproc"
        else:
            self.conf['postprocname'] = "postproc_"+self.conf['modelname']
        if self.conf['preprocname'] is None:
            if self.conf['modelname'] == "cosmo":
                self.conf['preprocname'] = "int2lm"
            else:
                self.conf['preprocname'] = "pre"+self.conf['modelname']
        #if self.conf['modelname'] == "icon":
        #    self.conf['getparentname'] = "get_parent_icon"

    def getconf(self):
        return self.conf

# Add a specific scheduling environment (sh, slurm or pbs) to a node.
class SchedEnv:
    def __init__(self, sched="sh"):
        self.sched = sched
    
    def add_to(self, node):
        if self.sched is not None:
            if self.sched == "pbs":
                node.add_variable("ECF_JOB_CMD", "qsub %EXTRA_SCHED:% %ECF_JOB%")
                node.add_variable("ECF_KILL_CMD", "qdel %ECF_RID%")
                node.add_variable("ECF_STATUS_CMD", "qstat %ECF_RID%")
            elif self.sched == "slurm":
                node.add_variable("ECF_JOB_CMD", "(date -u '+%%Y%%m%%d%%H%%M'; sbatch %EXTRA_SCHED:% %ECF_JOB%) >>%ECF_HOME%/sbatch.log 2>&1")
                node.add_variable("ECF_KILL_CMD", "scancel %ECF_RID%")
                node.add_variable("ECF_STATUS_CMD", "squeue -j %ECF_RID%")
            elif self.sched == "sh":
                node.add_variable("ECF_JOB_CMD", "%ECF_JOB% 1> %ECF_JOBOUT% 2>&1")
                node.add_variable("ECF_KILL_CMD", "kill -15 %ECF_RID%")
                node.add_variable("ECF_STATUS_CMD", "ps --sid %ECF_RID% -f")

# Add an observation data access family to a suite. To be called by
# WaitAndRun.
class GetObs:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        fam = node.add_family("get_obs") # experimental is it complete if empty?
        if self.conf['gts'] or self.conf['lhn'] or self.conf['radarvol']:
#            SchedEnv("sh").add_to(fam) # interactive because net access required for galileo
#            fam = node.add_family("get_obs")
            if self.conf['gts']: fam.add_task("get_gts")
            if self.conf['lhn']:
                if self.conf['preprocname'] == 'int2lm' and self.conf['membrange'] == [0]:
                    fam.add_task("get_radarlhn").add_variable("NO_FAIL", "TRUE").add_trigger('../eps_members/deterministic/preproc/merge_analysis == complete')
                else:
                    if self.conf['modelname'] == "icon":
                        fam.add_task("get_radarlhn_icon").add_variable("NO_FAIL", "TRUE")
                    else:
                        fam.add_task("get_radarlhn").add_variable("NO_FAIL", "TRUE")
            if self.conf['radarvol']: fam.add_task("get_radarvol")

# Add a model data access family to a suite. o be called by WaitAndRun.
class GetModel:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        fam = node.add_family("get_model")
        fam.add_task("get_model")

# Add a model preprocessing family to a node, to be called by EpsMembers.
class Preproc:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        fam = node.add_family("preproc")
        fam.add_trigger("./check_memb:required == 2")
        task = fam.add_task(self.conf['getparentname'])
        SchedEnv("sh").add_to(task) # interactive because net access required for galileo
        task = fam.add_task(self.conf['preprocname']).add_trigger("./"+self.conf['getparentname']+" == complete")
        if self.conf['preprocname'] == "int2lm":
            fam.add_task("merge_analysis").add_trigger("./"+self.conf['preprocname']+" == complete")
        elif self.conf['preprocname'] == "preicon":
            trig = "./"+self.conf['preprocname']+" == complete"
            if self.conf["radarvol"]: trig+= " && ../../../get_obs/get_radarvol == complete"
            fam.add_task("merge_analysis_icon").add_trigger(trig)

# Add a model run and postprocessing family to a node, to be called by
# EpsMembers.
class Model:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        fam = node.add_family("model")
        trig = "./preproc == complete"
        if GetObs in self.conf['runlist']: 
            if self.conf['modelname'] == "icon":
                if self.conf["lhn"]:      trig+= " && ../../get_obs/get_radarlhn_icon == complete"
#                if self.conf["radarvol"]: trig+= " && ../../get_obs/get_radarvol == complete"
            else:
                trig+= " && ../../get_obs == complete"
        fam.add_trigger(trig)
        fam.add_task(self.conf['modelname']).add_event("started")
        if self.conf['postproc']:
            if self.conf['postproctype'] == "async":
                     fam.add_task(self.conf['postprocname']).add_trigger("./"+self.conf['modelname']+":started == set")
            else:
# in this case WALL_TIME should be adapted (reduced)
                fam.add_task(self.conf['postprocname']).add_trigger("./"+self.conf['modelname']+" == complete")

# Add a set of ensemble model runs to a suite, including boundary and
# initial data access, data preprocessing and model run. Suitable also
# for deterministic runs, just by requesting one member. To be called
# by WaitAndRun.
class EpsMembers:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        ensfam = node.add_family("eps_members")
        for eps_memb in self.conf['membrange']:
            if eps_memb == -1:
                fname = "control" # control
            elif eps_memb == 0:
                fname = "deterministic" # deterministic
            else:
                fname = "eps_member_"+str(eps_memb)
            self.conf['postproc'] = (eps_memb in self.conf['postprocrange'])
            fam = ensfam.add_family(fname)
            fam.add_complete(fname+"/check_memb:required == 1")
            fam.add_variable("ECF_ENS_MEMB", str(eps_memb))
            if self.conf['nofail']:
                fam.add_variable("NO_FAIL", "TRUE") # do not fail in case of error
            task = fam.add_task("check_memb").add_meter("required", 0, 2)
            SchedEnv(sched="sh").add_to(task)
            Preproc(self.conf).add_to(fam)
            Model(self.conf).add_to(fam)

            wipe = fam.add_family("wipe")
            SchedEnv(sched="sh").add_to(wipe)
            timerdep = ""
            if self.conf['timer'] is not None:
                task = wipe.add_task("wipe_timer")
                task.add_complete("./wipe_member == complete")
                task.add_time(self.conf['timer'])
                task.add_variable("ECF_DUMMY_TASK","Y")
                timerdep = " || ./wipe_timer == complete"

            task = wipe.add_task("wipe_member")
            task.add_complete("../model == complete")
            task.add_trigger("../model == aborted || ../preproc == aborted || ../check_memb == aborted"+timerdep)

# Add a verification family to the suite, to be run after the ensemble model run
class Verification:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        fam = node.add_family("verification")
        fam.add_trigger("./get_model == complete && ./get_obs == complete")
        task_mec = fam.add_task("mec_verif")

# Add an ensemble data assimilation family to a suite, to be run
# collectively after the ensemble model run, tailored for kenda. To be
# called by WaitAndRun.
class EndaAnalysis:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        fam = node.add_family("enda_analysis")
        fam.add_trigger("./eps_members == complete && ./get_obs == complete")
        if self.conf['modelname'] == "icon":
            task = fam.add_task("mec")
            fam.add_task("prepare_kenda_icon").add_trigger("./mec == complete")
            task = fam.add_task("kenda").add_trigger("./prepare_kenda_icon == complete")
            task = fam.add_task("archive_kenda_icon").add_trigger("./kenda == complete")
        else:
            fam.add_task("prepare_kenda")
            task = fam.add_task("kenda").add_trigger("./prepare_kenda == complete")
            fam.add_task("archive_kenda").add_trigger("./kenda == complete")

# Add a continuous analysis step to a suite, to be run after model
# run, it has a simpler structure than enda family. To be called by
# WaitAndRun.
class ContinuousAnalysis:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        fam = node.add_family("continuous_analysis")
        fam.add_trigger("./eps_members == complete")
        fam.add_task("archive_analysis")

# Add an eps postproc family to a suite, tipically for computation of
# collective probabilities after the ensemble run. To be called by
# WaitAndRun.
class EpsPostproc:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        fam = node.add_family("eps_postproc")
        fam.add_trigger("./eps_members == complete")
        if self.conf["epspostproclevel"] == 1:
            fam.add_task("compute_prob")
            fam.add_task("upload_prob").add_trigger("./compute_prob == complete")
        elif self.conf["epspostproclevel"] == 2:
            cp = fam.add_task("compute_probs")
            cp.add_meter("n_members", 0, max(self.conf['membrange']), 0)
            cp.add_event("main_prob")
            cp.add_event("extra_prob")
            cp.add_event("tp_acc")
            fam.add_task("scacchiera_tp").add_trigger("./compute_probs:tp_acc == set")
            fam.add_task("scacchiera_ensmean").add_trigger("./compute_probs:main_prob == set")
            fam.add_task("scacchiera_prob").add_trigger("./compute_probs:main_prob == set")
            fam.add_task("mappe_eps").add_trigger("./compute_probs:main_prob == set and ./compute_probs:extra_prob == set")
            fam.add_task("upload_probs").add_trigger("./compute_probs == complete and ./scacchiera_tp == complete and ./scacchiera_ensmean == complete and ./scacchiera_prob == complete and ./mappe_eps == complete")

# Add family for the diagnostic of KENDA
class EndaDiagnostics:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        fam = node.add_family("enda_diagnostics")
        fam.add_task("diagnostic_ekf")

# Add a wipe family containing a single task wipe; wipe should set run
# family to complete, possibly with more fine-grain control on tasks,
# and exiting thus resubmitting the suite for next run. To be called
# by WaitAndRun.
class WipeRun:
    def __init__(self, conf={}):
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        timerdep = ""
        if self.conf['timer'] is not None:
            task = wipe.add_task("wipe_timer")
            task.add_complete("./wipe_run == complete")
            task.add_time(self.conf['timer'])
            task.add_variable("ECF_DUMMY_TASK","Y")
            timerdep = "./wipe_timer == complete"

        trig = ""
        if GetObs in self.conf['runlist']:
            trig = expr_or(trig, "../run/get_obs == aborted")
        if GetModel in self.conf['runlist']:
            trig = expr_or(trig, "../run/get_model == aborted")
        if Verification in self.conf['runlist']:
            trig = expr_or(trig, "../run/verification == aborted")
        if EndaAnalysis in self.conf['runlist']:
            trig = expr_or(trig, "../run/enda_analysis == aborted")
        if ContinuousAnalysis in self.conf['runlist']:
            trig = expr_or(trig, "../run/continuous_analysis == aborted")
        if EpsPostproc in self.conf['runlist']:
            trig = expr_or(trig, "../run/eps_postproc == aborted")
        if EndaDiagnostics in self.conf['runlist']:
            trig = expr_or(trig, "../run/enda_diagnostics == aborted")

        fulldep = expr_or(trig, timerdep)
        if fulldep != "":
            wipe = node.add_family("wipe")
            SchedEnv(sched="sh").add_to(wipe)
            task = wipe.add_task("wipe_run")
            task.add_complete("../run == complete")
            task.add_trigger(fulldep) # || ../check_run == aborted")

        # Add variable to recognize the use of radar volumes
        if self.conf["radarvol"]:
            node.add_variable("RADVOL", "Y")
        else:
            node.add_variable("RADVOL", "N")

# Add basic environment (suite definition variables) to a suite node,
# usually to root node.
class BasicEnv():
    def __init__(self, srctree=None, worktree=None, sched=None, client_wrap="", ntries=1, extra_env=None):
        self.srctree = srctree
        self.worktree = worktree
        self.sched = sched
        if client_wrap == "": self.ecflow_client = "ecflow_client"
        else: self.ecflow_client = client_wrap+" ecflow_client"
        self.ntries = ntries
        self.extra_env = extra_env

    def add_to(self, node):
        if self.sched is not None:
            sched_suff = "_"+self.sched
        else:
            sched_suff = ""
        node.add_variable("ECF_INCLUDE", os.path.join(self.srctree,"ecflow","include"+sched_suff))
        node.add_variable("ECF_FILES", os.path.join(self.srctree,"ecflow","jobs"))
        node.add_variable("BASEDIR", self.srctree)
        node.add_variable("ECF_HOME", self.worktree)
        node.add_variable("ecflow_client", self.ecflow_client)
        node.add_variable("ECF_TRIES", str(self.ntries))
        SchedEnv(sched=self.sched).add_to(node)
        if self.extra_env is not None:
            for var in self.extra_env:
                node.add_variable(var, self.extra_env[var])

# Add a complete wait and run family to a suite, to be called directly
# by the user, to be added somewhere near the root of the suite.
class WaitAndRun:
    def __init__(self, dep=None, conf={}):
        self.dep = dep
        self.conf = {}
        self.conf.update(conf)

    def add_to(self, node):
        if self.conf['startmethod'] == "check_run":
            fam = node.add_family("check_run")
            SchedEnv("sh").add_to(fam)

            fam.add_complete("check_run/can_run == complete")
            # first task
            task = fam.add_task("can_run")
            task.add_trigger("check_run:checked")
            task.add_event("ready")
            # second task
            task = fam.add_task("check_run")
            task.add_complete("can_run:ready")
            task.add_cron(daily_cron(self.conf['cronfreq']))
            if self.dep is not None:
                task.add_trigger("../../"+self.dep+" == complete")
            task.add_event("checked")

            fam = node.add_family("run")
            fam.add_trigger("check_run == complete")

        elif self.conf['startmethod'] == "continuous":
            fam = node.add_family("run")
            if self.dep is not None:
                fam.add_trigger("../"+self.dep+" == complete")

        elif self.conf['startmethod'] == "manual":
            task = node.add_task("continue")
            task.add_variable("ECF_DUMMY_TASK","Y")
            fam = node.add_family("run")
            if self.dep is not None:
                fam.add_trigger("../"+self.dep+" == complete && ./continue == complete")
            else:
                fam.add_trigger("./continue == complete")

        elif self.conf['startmethod'] == "starttime_time":
            fam = node.add_family("run")
            if self.dep is not None:
                fam.add_trigger("../"+self.dep+" == complete")
            fam.add_time(self.conf['starttime'])                    # UTC time

        elif self.conf['startmethod'] == "starttime_cron":
            fam = node.add_family("run")
            if self.dep is not None:
                fam.add_trigger("../"+self.dep+" == complete")
            fam.add_cron(cron_set_time(self.conf['starttime']))     # UTC time

        # instantiate with general configuration and add all
        # components of runlist
        if self.conf['runlist'] is not None:
            for run in self.conf['runlist']:
                run(self.conf).add_to(fam)
        WipeRun(self.conf).add_to(node)

# Create a model suite to be filled through WaitAndRun class, add
# limits then check it and load it on the server.
class ModelSuite():
    def __init__(self, name):
        self.name = name
        self.defs = ecflow.Defs()
        self.suite = self.defs.add_suite(name)
        self.checked = False


    def addlimit(self, name, size, nodere):
        import re
        noderec = re.compile(nodere)
#        for suite in self.defs.suites:
        self.suite.add_limit(name, size) # add limit at suite root level
        self.__loopnodes(self.suite, name, noderec)


    def __loopnodes(self, suite, name, noderec):
        for node in suite.nodes:
            if isinstance(node, ecflow.Task): # task, stop here
                if noderec.search(node.name()):
                    node.add_inlimit(name, "", 1)
            else: # family, go deeper
                if noderec.search(node.name()):
                    node.add_inlimit(name, "", 1)
                else: # do not go deeper if the limit applies to the family
                    self.__loopnodes(node, name, noderec)


    def check(self):
        # check syntax
        result = self.defs.check()
        if result != "":
            print("Error in "+self.name+" suite definition:")
            print(result)
        else:
            # check job tree
            result = self.defs.check_job_creation()
            if result != "":
                print("Error in "+self.name+" suite job creation:")
                print(result)
            else: 
                self.checked = True


    def write(self, interactive=True):
        if not self.checked:
            print("suite "+self.name+" has not been checked, refusing to write")
            return
        name = self.name+".def"
        if interactive:
            if os.path.exists(name):
                if not ask_confirm("Definition file "+name+" exists, replace"):
                    return
        self.defs.save_as_defs(name)
        print("Suite saved in "+name)


    def replace(self, interactive=True):
        if not self.checked:
            print("suite "+self.name+" has not been checked, refusing to replace")
            return
        if interactive:
            if not ask_confirm("Replace suite "+self.name+" on server"):
                return
        client = ecflow.Client() # connect using environment
        client.replace("/"+self.name, self.defs)
        print("Suite "+self.name+" replaced on server")
