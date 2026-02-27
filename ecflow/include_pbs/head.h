set -e          # stop the shell on first error
#set -u          # fail when using an undefined variable
#set -x          # echo script lines as they are executed
set -o pipefail # fail if last(rightmost) command exits with a non-zero status


# Defines the variables that are needed for any communication with ECF
export ECF_PORT=%ECF_PORT%    # The server port number
export ECF_HOST=%ECF_HOST%    # The host name where the server is running
export ECF_NAME=%ECF_NAME%    # The name of this current task
export ECF_PASS=%ECF_PASS%    # A unique password
export ECF_TRYNO=%ECF_TRYNO%  # Current try number of the task
export ECF_DENIED=%ECF_DENIED:% # Optional, if set, ecflow_client exits when connection with server fails

# Record the process id. Also used for zombie detection
if [ -n "$PBS_JOBID" ]; then
    export ECF_RID=${PBS_JOBID%%.*}
elif [ -n "$SLURM_JOB_ID" ]; then
    export ECF_RID=$SLURM_JOB_ID
else
    export ECF_RID=$$
fi

# Wrapper for calling ecflow_client
export ecflow_client="%ecflow_client%"

# Set ensemble member from ecflow if available
if [ -z "$ENS_MEMB" ]; then
    export ENS_MEMB=%ECF_ENS_MEMB:0%
fi
if [ "$ENS_MEMB" = 0 ]; then
    unset ENS_MEMB
fi
# >0 ensemble member
# 0 deterministic
# -1 control
# -2 loop on all members from 0 to $ENS_TOTAL_MEMB


# Tell ecFlow we have started
$ecflow_client --init=$ECF_RID

# Define error and exit handlers
ERROR() {
    set +e                      # Clear -e flag, so we don't fail
    wait                        # wait for background process to stop
    if [ "%NO_FAIL:%" = "TRUE" ]; then
    $ecflow_client --msg="Forgiving failure of %ECF_NAME%"
    $ecflow_client --complete   # Notify ecFlow of a normal end
    else
    $ecflow_client --abort=trap # Notify ecFlow that something went wrong, using 'trap' as the reason
    fi
    trap - EXIT ERR             # Remove the trap
    exit 0                      # End the script, was exit 1, set to 0 to avoid double failure of interactive jobs
}
 
CLEANEXIT() {
    [ "$?" = "0" ] || ERROR   # required for `exit 1` to call ERROR function
    wait                      # wait for background process to stop
    $ecflow_client --complete # Notify ecFlow of a normal end
    trap - EXIT               # Remove all traps
    exit 0                    # End the script
}


# Trap any calls to exit and errors caught by the -e flag
#trap ERROR 0


# Trap any signal that may cause the script to fail
trap '{ CLEANEXIT ; }' EXIT
trap '{ echo "Exiting with error"; ERROR ; }' ERR
trap '{ echo "Killed by a signal"; ERROR ; }' 1 2 3 4 5 6 7 8 10 12 13 15


# Optional nwpconf setup, NWPCONF comes from the suite def
export NWPCONF=%NWPCONF:%
if [ -n "$NWPCONF" ]; then
    export NWPCONFDIR=%BASEDIR%/conf
    export NWPCONFBINDIR=%BASEDIR%/libexec/nwpconf
    export DATE=%YMD:%
    export TIME=%TIME:00%

# Source the main nwpconf library module, other modules must be sourced
# in the job
    . $NWPCONFBINDIR/nwpconf.sh
fi
