#!/usr/bin/python3

import os,sys
import datetime
import optparse
import ecflow
from nwprun import *

parser = optparse.OptionParser(usage="%prog [OPTIONS]")
parser.add_option("--yes", help="work in non-interactive mode and answer yes to all questions (it will overwrite files and replace scripts on server)",
                  action="store_true")
parser.add_option("--delta", help="comma-separated list of delta time in days to go back, for each suite",
                  default="0,0,0,0")

opts, args = parser.parse_args()
interactive = not opts.yes
delta = [int(i) for i in opts.delta.split(',')]

hpcenv = os.environ["HPC_SYSTEM"]
common_extra_env = {
    "NO_FAIL": "FALSE",
    "TASK_PER_CORE": "1",
    "HPCENV": os.environ["HPC_SYSTEM"],
    "ECF_TIMEOUT": "7200",
    "ECF_DENIED": "",
    "WALL_TIME_WAIT": "04:10:00",
    "WALL_TIME_ARCHIVE": "04:10:00"
}

# Suite enda
extra_env = common_extra_env.copy()
if hpcenv == "leonardo":
    extra_env.update({
        "NWPCONF": "prod/icon_2I/enda",
        "NNODES_PREMODEL": 1,
        "NNODES_MODEL": 2,
        "NNODES_ENDA": 6,
        "NNODES_MEC": 6,
        "NTASKS_POSTPROC": 2,
        "WALL_TIME_PREMODEL": "00:20:00",
        "WALL_TIME_MODEL": "00:20:00",
        "WALL_TIME_ENDA": "00:30:00",
        "WALL_TIME_MEC": "00:30:00"
    })
else: #default g100
    extra_env.update({
        "NWPCONF": "prod/icon_2I/enda",
        "NNODES_PREMODEL": 1,
        "NNODES_MODEL": 3,
        "NNODES_ENDA": 8,
        "NNODES_MEC": 8,
        "NTASKS_POSTPROC": 2,
        "WALL_TIME_PREMODEL": "00:20:00",
        "WALL_TIME_MODEL": "00:20:00",
        "WALL_TIME_ENDA": "00:30:00",
        "WALL_TIME_MEC": "00:30:00"
    })
basicenv = BasicEnv(srctree=os.path.join(os.environ["WORKDIR_BASE"], "nwprun"),
                    worktree=os.path.join(os.environ["WORKDIR_BASE"], "ecflow"),
                    sched="slurm",
                    client_wrap=os.path.join(os.environ["WORKDIR_BASE"], "nwprun","ecflow","ec_wrap"),
                    ntries=2,
                    extra_env=extra_env)

conf = ModelConfig({"gts": True, "lhn": True, "radarvol": True, "membrange": "0-40",
                    "postprocrange": "0",
                    "modelname": "icon",
                    "runlist": [GetObs, EpsMembers, EndaAnalysis]}).getconf()
enda = ModelSuite("icon_2I_enda")
basicenv.add_to(enda.suite)
day = enda.suite.add_family("day").add_repeat(
    ecflow.RepeatDate("YMD", 
                      int((datetime.datetime.now()-datetime.timedelta(days=delta[0])).strftime("%Y%m%d")),
                      20301228))

hdep = None # first repetition has no dependency
for h in range(0, 24, 1):
    famname = "hour_" + ("%02d" % h)
    hour = day.add_family(famname).add_variable("TIME", "%02d" % h)
    #    hrun = "%02d:00" % (h+1 % 24) # start 1h after nominal time
    WaitAndRun(dep=hdep, conf=conf).add_to(hour)
    hdep = famname # dependency for next repetition

enda.check()
enda.write(interactive=interactive)
enda.replace(interactive=interactive)


# Suite icon fcast
extra_env = common_extra_env.copy()
if hpcenv == "leonardo":
    extra_env.update({
        "NWPCONF": "prod/icon_2I/fcast",
        "NNODES_PREMODEL": 2,
        "NNODES_MODEL": 12,
        "NTASKS_POSTPROC": 2,
        "WALL_TIME_PREMODEL": "00:20:00",
        "WALL_TIME_MODEL": "02:00:00"
    })
else: # default g100
    extra_env.update({
        "NWPCONF": "prod/icon_2I/fcast",
        "NNODES_PREMODEL": 2,
        "NNODES_MODEL": 16,
        "NTASKS_POSTPROC": 2,
        "WALL_TIME_PREMODEL": "00:20:00",
        "WALL_TIME_MODEL": "02:00:00"
    })
basicenv = BasicEnv(srctree=os.path.join(os.environ["WORKDIR_BASE"], "nwprun"),
                    worktree=os.path.join(os.environ["WORKDIR_BASE"], "ecflow"),
                    sched="slurm",
                    client_wrap=os.path.join(os.environ["WORKDIR_BASE"], "nwprun","ecflow","ec_wrap"),
                    ntries=2,
                    extra_env=extra_env)

conf = ModelConfig({"gts": False, "lhn": True, "membrange": "0",
                    "postprocrange": "0",
                    "startmethod": "manual",
                    "modelname": "icon", 
                    "runlist": [GetObs, EpsMembers]}).getconf()
icon = ModelSuite("icon_2I_fcast")
basicenv.add_to(icon.suite)
day = icon.suite.add_family("day").add_repeat(
    ecflow.RepeatDate("YMD", 
                      int((datetime.datetime.now()-datetime.timedelta(days=delta[1])).strftime("%Y%m%d")),
                      20301228))

hdep = None # first repetition has no dependency
for h in range(0, 24, 12):
    famname = "hour_" + ("%02d" % h)
    hour = day.add_family(famname).add_variable("TIME", "%02d" % h)
    #    hrun = "%02d:00" % (h+1 % 24) # start 1h after nominal time
    WaitAndRun(dep=hdep, conf=conf).add_to(hour)
    hdep = famname # dependency for next repetition

icon.check()
icon.write(interactive=interactive)
icon.replace(interactive=interactive)


# Suite icon fcruc
extra_env = common_extra_env.copy()
extra_env.update({
    "NWPCONF": "prod/icon_2I/fcruc",
    "NNODES_PREMODEL": 3,
    "NNODES_MODEL": 16,
    "NTASKS_POSTPROC": 2,
    "WALL_TIME_PREMODEL": "00:20:00",
    "WALL_TIME_MODEL": "01:00:00"
})
basicenv = BasicEnv(srctree=os.path.join(os.environ["WORKDIR_BASE"], "nwprun"),
                    worktree=os.path.join(os.environ["WORKDIR_BASE"], "ecflow"),
                    sched="slurm",
                    client_wrap=os.path.join(os.environ["WORKDIR_BASE"], "nwprun","ecflow","ec_wrap"),
                    ntries=2,
                    extra_env=extra_env)

conf = ModelConfig({"gts": False, "lhn": True, "membrange": "0",
                    "postprocrange": "0",
                    "modelname": "icon", 
                    "runlist": [GetObs, EpsMembers]}).getconf()
icon = ModelSuite("icon_2I_fcruc")
basicenv.add_to(icon.suite)
day = icon.suite.add_family("day").add_repeat(
    ecflow.RepeatDate("YMD", 
                      int((datetime.datetime.now()-datetime.timedelta(days=delta[1])).strftime("%Y%m%d")),
                      20301228))

hdep = None # first repetition has no dependency
for h in range(0, 24, 3): # 3,6,9,15,18,21:
    famname = "hour_" + ("%02d" % h)
    hour = day.add_family(famname).add_variable("TIME", "%02d" % h)
    #    hrun = "%02d:00" % (h+1 % 24) # start 1h after nominal time
    WaitAndRun(dep=hdep, conf=conf).add_to(hour)
    hdep = famname # dependency for next repetition

icon.check()
icon.write(interactive=interactive)
icon.replace(interactive=interactive)


# Suite fcens
extra_env = common_extra_env.copy()
if hpcenv == "leonardo":
    extra_env.update({
        "NWPCONF": "prod/icon_2I/fcens",
        "NNODES_PREMODEL": 3,
        "NNODES_MODEL": 6,
        "NNODES_ENDA": 6,
        "NTASKS_POSTPROC": 2,
        "WALL_TIME_PREMODEL": "00:20:00",
        "WALL_TIME_MODEL": "02:00:00",
        "ECF_TIMEOUT": "14400"
    })
else: #default g100
    extra_env.update({
        "NWPCONF": "prod/icon_2I/fcens",
        "NNODES_PREMODEL": 3,
        "NNODES_MODEL": 6,
        "NNODES_ENDA": 6,
        "NTASKS_POSTPROC": 2,
        "WALL_TIME_PREMODEL": "00:20:00",
        "WALL_TIME_MODEL": "03:00:00",
        "ECF_TIMEOUT": "14400"
    })

basicenv = BasicEnv(srctree=os.environ["OPE"],
                    worktree=os.path.join(os.environ["WORKDIR_BASE"], "ecflow"),
                    sched="slurm",
                    client_wrap=os.path.join(os.environ["OPE"],"ecflow","ec_wrap"),
                    ntries=2,
                    extra_env=extra_env)

conf = ModelConfig({"gts": False, "lhn": True, "membrange": "1-20",
                    "postprocrange": "1-20",
                    "modelname": "icon",
                    "runlist": [GetObs, EpsMembers, EpsPostproc],
                    "epspostproclevel": 2}).getconf()
fcens = ModelSuite("icon_2I_fcens")
basicenv.add_to(fcens.suite)
day = fcens.suite.add_family("day").add_repeat(
    ecflow.RepeatDate("YMD",
                      int((datetime.datetime.now()-datetime.timedelta(days=delta[2])).strftime("%Y%m%d")),
                      20301228))
hdep = None # first repetition has no dependency
for h in range(21, 24, 3): # h=21
    famname = "hour_" + ("%02d" % h)
    hour = day.add_family(famname).add_variable("TIME", "%02d" % h)
    #    hrun = "%02d:00" % (h+1 % 24) # start 1h after nominal time
    WaitAndRun(dep=hdep, conf=conf).add_to(hour)
    hdep = famname # dependency for next repetition

fcens.check()
fcens.write(interactive=interactive)
fcens.replace(interactive=interactive)


# Suite enda_dia
extra_env = common_extra_env.copy()
extra_env.update({
    "NWPCONF": "prod/icon_2I/enda_dia",
})
basicenv = BasicEnv(srctree=os.path.join(os.environ["WORKDIR_BASE"], "nwprun"),
                    worktree=os.path.join(os.environ["WORKDIR_BASE"], "ecflow"),
                    sched="slurm",
                    client_wrap=os.path.join(os.environ["WORKDIR_BASE"], "nwprun","ecflow","ec_wrap"),
                    ntries=2,
                    extra_env=extra_env)

conf = ModelConfig({"runlist": [EndaDiagnostics], "startmethod": "starttime_cron",
                    "starttime": "06:30"}).getconf()
enda_dia = ModelSuite("icon_2I_enda_dia")
basicenv.add_to(enda_dia.suite)
WaitAndRun(dep=None, conf=conf).add_to(enda_dia.suite)

enda_dia.check()
enda_dia.write(interactive=interactive)
enda_dia.replace(interactive=interactive)


# Suite icon verif_mod
extra_env = common_extra_env.copy()
extra_env.update({
    "NWPCONF": "prod/icon_2I/verif_mod",
    "NNODES_MEC": 6,
    "WALL_TIME_MEC": "00:30:00"
})
basicenv = BasicEnv(srctree=os.path.join(os.environ["WORKDIR_BASE"], "nwprun"),
                    worktree=os.path.join(os.environ["WORKDIR_BASE"], "ecflow"),
                    sched="slurm",
                    client_wrap=os.path.join(os.environ["WORKDIR_BASE"], "nwprun","ecflow","ec_wrap"),
                    ntries=2,
                    extra_env=extra_env)

conf = ModelConfig({"gts": True, "lhn": False, "membrange": "0", "modelname": "icon",
                    "runlist": [GetObs, GetModel, Verification]}).getconf()
icon = ModelSuite("icon_2I_verif_mod")
basicenv.add_to(icon.suite)
day = icon.suite.add_family("day").add_repeat(
    ecflow.RepeatDate("YMD",
                      int((datetime.datetime.now()-datetime.timedelta(days=delta[3])).strftime("%Y%m%d")),
                      20301228))

hdep = None # first repetition has no dependency
for h in range(0, 24, 12):
    famname = "hour_" + ("%02d" % h)
    hour = day.add_family(famname).add_variable("TIME", "%02d" % h)
    #    hrun = "%02d:00" % (h+1 % 24) # start 1h after nominal time
    WaitAndRun(dep=hdep, conf=conf).add_to(hour)
    hdep = famname # dependency for next repetition

icon.check()
icon.write(interactive=interactive)
icon.replace(interactive=interactive)


# Suite icon verif_obs
extra_env = common_extra_env.copy()
extra_env.update({
    "NWPCONF": "prod/icon_2I/verif_obs",
    "NNODES_MEC": 6,
    "WALL_TIME_MEC": "00:30:00"
})
basicenv = BasicEnv(srctree=os.path.join(os.environ["WORKDIR_BASE"], "nwprun"),
                    worktree=os.path.join(os.environ["WORKDIR_BASE"], "ecflow"),
                    sched="slurm",
                    client_wrap=os.path.join(os.environ["WORKDIR_BASE"], "nwprun","ecflow","ec_wrap"),
                    ntries=2,
                    extra_env=extra_env)

conf = ModelConfig({"gts": True, "lhn": False, "membrange": "0", "modelname": "icon",
                    "runlist": [GetObs, GetModel, Verification]}).getconf()
icon = ModelSuite("icon_2I_verif_obs")
basicenv.add_to(icon.suite)
day = icon.suite.add_family("day").add_repeat(
    ecflow.RepeatDate("YMD",
                      int((datetime.datetime.now()-datetime.timedelta(days=delta[3])).strftime("%Y%m%d")),
                      20301228))

hdep = None # first repetition has no dependency
for h in range(0, 24, 1):
    famname = "hour_" + ("%02d" % h)
    hour = day.add_family(famname).add_variable("TIME", "%02d" % h)
    #    hrun = "%02d:00" % (h+1 % 24) # start 1h after nominal time
    WaitAndRun(dep=hdep, conf=conf).add_to(hour)
    hdep = famname # dependency for next repetition

icon.check()
icon.write(interactive=interactive)
icon.replace(interactive=interactive)


# Suite ifs verif_obs
extra_env = common_extra_env.copy()
extra_env.update({
    "NWPCONF": "prod/ifs/verif_obs",
    "NNODES_MEC": 6,
    "WALL_TIME_MEC": "00:30:00"
})
basicenv = BasicEnv(srctree=os.path.join(os.environ["WORKDIR_BASE"], "nwprun"),
                    worktree=os.path.join(os.environ["WORKDIR_BASE"], "ecflow"),
                    sched="slurm",
                    client_wrap=os.path.join(os.environ["WORKDIR_BASE"], "nwprun","ecflow","ec_wrap"),
                    ntries=2,
                    extra_env=extra_env)

conf = ModelConfig({"gts": True, "lhn": False, "membrange": "0", "modelname": "ifs",
                    "runlist": [GetObs, GetModel, Verification]}).getconf()
ifs = ModelSuite("ifs_verif_obs")
basicenv.add_to(ifs.suite)
day = ifs.suite.add_family("day").add_repeat(
    ecflow.RepeatDate("YMD",
#                      int((datetime.datetime.now()-datetime.timedelta(days=delta[3])).strftime("%Y%m%d")),
                      20240711,
                      20301228))

hdep = None # first repetition has no dependency
for h in range(0, 24, 1):
    famname = "hour_" + ("%02d" % h)
    hour = day.add_family(famname).add_variable("TIME", "%02d" % h)
    #    hrun = "%02d:00" % (h+1 % 24) # start 1h after nominal time
    WaitAndRun(dep=hdep, conf=conf).add_to(hour)
    hdep = famname # dependency for next repetition

ifs.check()
ifs.write(interactive=interactive)
ifs.replace(interactive=interactive)

