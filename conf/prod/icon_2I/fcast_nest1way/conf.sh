# Model environment variables
#MODEL_BASE=$WORKDIR_BASE/srcintel/icon-nwp_terra-urb-2025-11-13
MODEL_BASE=/ind2/meteo/a07smr03/lami/srcintel/icon_2025-04-1
MODEL_BIN=$MODEL_BASE/bin/icon
MODEL_STATIC=$WORKDIR_BASE/data/icon

# Parent model environment variables
PARENTMODEL=ICON
PARENTMODEL_ARKI_DS=$WORKDIR_BASE/arkimet/icon_icbc2Iglbtuoff
#PARENTMODEL_SIGNAL=hres_am_foricon
PARENTMODEL_FREQINI=6
PARENTMODEL_FREQANA=6
PARENTMODEL_FREQFC=1
#Il parent model in questo caso è : icbc2Ieco
PARENTMODEL_DOMAIN=Nest500_from_OPE2km_to_EM500m_GLBC_v1
PARENTMODEL_STATIC=$MODEL_STATIC/domain_$PARENTMODEL_DOMAIN
PARENTMODEL_GRIDFILE=${PARENTMODEL_DOMAIN}_DOM01.nc 
PARENTMODEL_STATICFILE=${PARENTMODEL_DOMAIN}_DOM01_external_parameter.nc 



# ICON-2I domain and grid files #LUDO
DOMAIN=Nest500_from_EM500mv1_to_EM125m_GLBC_v0
LOCALGRID=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM01.nc
LOCALGRID_PARENT=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM01.parent.nc
LOCALGRID_EXTERNAL=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM01_external_parameter.nc

# Time step 10 per 1 km
TIME_STEP=5

# invent W_SO_ICE and FR_ICE and set them to 0
#ADD_ICE_FIELDS=Y

# Model environment variables
MODEL_BACK=0
MODEL_STOP=24
MODEL_BCANA=N
MODEL_FREQINI=12
ENS_TOTAL_MEMB=0
# Time difference between model and parent reftime 
MODEL_DELTABD=0
# Number of boundary conditions handled by each task
NBC_PER_TASK=1

# Latent Heat Nudging (LHN)
MODEL_LHN=.FALSE. #LUDO: can be false
MODEL_NH_LHN=4

# MEC verification (modified version of executables)
DACE_BASE=/g100_work/smr_prod/srcintel_thomas/dace_code_2.06_mec
MEC_BIN=$DACE_BASE/build/LINUX64.intel-mpi/bin/mec
MEC_WORKDIR=$WORKDIR/mec
LETKF_CONST=$DACE_BASE/data

# setup for arkilocal
ARKI_DIR=$WORKDIR/arki
# setup for remote import
unset ARKI_IMPDIR
ARKI_SYNCDIR=$WORKDIR_BASE/import/sync.lami
ARKI_DLDIR=$WORKDIR_BASE/download
unset ARKI_SYNCDIR
unset ARKI_DLDIR
CROSS_NETWORK=icon_2I_fcast_c
VPROF_NETWORK=icon_2I_fcast_v
unset CROSS_NETWORK
unset VPROF_NETWORK
MODEL_SIGNAL=icon_2I_fcast_urb #LUDO: added _urb after test 20251216. No further tests this day

# suite timing
NWPWAITELAPS=14400
# differenza tra tempo nominale e tempo di attivazione della suite
NWPWAITSOLAR_RUN=1800
# dopo quando tempo rinuncio a girare la suite e passare alla successiva
NWPWAITSOLAR=14400
NWPWAITWAIT=60
# wait for analysis?
WAIT_ANALYSIS=N
#READY_FILE_DELAY=40
# to be removed
#STOP_ON_FAIL=Y
