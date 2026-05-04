###
#  CONF MODELLO OPE, DOMINIO NEST500_v1, 24H
###
# Model environment variables
#MODEL_BASE=$WORKDIR_BASE/srcintel/icon-nwp_terra-urb-2025-11-13i
MODEL_BIN=$MODEL_BASE/bin/icon
MODEL_STATIC=$WORKDIR_BASE/data/icon

# Parent model environment variables
PARENTMODEL=IFS
PARENTMODEL_ARKI_DS=$ARKI_DIR/hres_am_foricon
#PARENTMODEL_SIGNAL=hres_am_foricon
PARENTMODEL_FREQINI=6
PARENTMODEL_FREQANA=6
PARENTMODEL_FREQFC=1

# ICON-2I domain and grid files #LUDO
DOMAIN=Nest500_from_OPE2km_to_EM500m_GLBC_v1
#L: ICON-D3_DOM01       ICON-D2_DOM01_b.nc
LOCALGRID=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM01.nc
LOCALGRID_PARENT=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM01.parent.nc
LOCALGRID_EXTERNAL=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM01_external_parameter.nc
#L: ${DOMAIN}_external_parameter.nc  

# Time step 20 per 5 km
TIME_STEP=20

# Model environment variables
MODEL_BACK=0
MODEL_STOP=1
MODEL_BCANA=N
MODEL_FREQINI=12
ENS_TOTAL_MEMB=0
MODEL_ARCHIVE_ANA=$WORKDIR/../enda/archive

# Time difference between model and parent reftime 
case $TIME in
    03 | 09 | 15 | 21)
        MODEL_DELTABD=0 #was 9
        ;;
    00 | 06 | 12 | 18)
        MODEL_DELTABD=0 #was 6
esac

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
WAIT_ANALYSIS=Y
