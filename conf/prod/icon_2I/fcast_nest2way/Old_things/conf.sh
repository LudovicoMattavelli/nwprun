# Model environment variables
MODEL_BASE=$WORKDIR_BASE/srcintel/icon-nwp_terra-urb-2025-11-13
#icon-nwp_terra-urb-2025-11-13
#MODEL_BASE=/ind2/meteo/a07smr03/lami/srcintel/icon_2024-10
MODEL_BIN=$MODEL_BASE/bin/icon
#MODEL_STATIC=$WORKDIR_BASE/data/icon
ECRAD_DATA=$MODEL_BASE/data
#MODEL_PRE_BINDIR=/ind2/meteo/a07smr03/lami/srcintel/icontools-2.5.0/icontools #L20251218: li lascio o li tolgo?
#PARENTMODEL_DATADIR=$WORKDIR/input/data #L20251218: idem

# Parent model environment variables
PARENTMODEL=IFS
PARENTMODEL_ARKI_DS=$ARKI_DIR/hres_am_foricon
PARENTMODEL_SIGNAL=hres_am_foricon
PARENTMODEL_FREQINI=6
PARENTMODEL_FREQANA=6
PARENTMODEL_FREQFC=1

# Grid
MODEL_STATIC=$WORKDIR_BASE/data/icon
NESTING=Y
#MODEL_STATIC=/g100_work/smr_prod/data
DOMAIN=Nest500_from_OPE2km_to_EM500m_v1
LOCALGRID=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM01.nc
LOCALGRID_NEST=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM02.nc
LOCALGRID_NEST_NEST=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM03.nc # Aggiunto per n500m
LOCALGRID_PARENT=$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM01.parent.nc
LOCALGRID_EXTERNAL_PATH=$MODEL_STATIC/domain_$DOMAIN
LOCALGRID_EXTERNAL="$MODEL_STATIC/domain_$DOMAIN/${DOMAIN}_DOM<idom>_external_parameter.nc"

# Model environment variables
MODEL_BACK=0
MODEL_STOP=12
MODEL_BCANA=N
MODEL_FREQINI=12
ENS_TOTAL_MEMB=0
MODEL_ARCHIVE_ANA=$WORKDIR/../enda_ope_ng/file_salvati

# Time difference between model and parent reftime # L251219 metto a 0?
case $TIME in
    03 | 09 | 15 | 21)
        MODEL_DELTABD=9
        ;;
    00 | 06 | 12 | 18)
        MODEL_DELTABD=6
esac

# Number of boundary conditions handled by each task
NBC_PER_TASK=1

# Latent Heat Nudging (LHN)
MODEL_LHN=.FALSE.
MODEL_NH_LHN=4

# MEC verification (modified version of executables)
#DACE_BASE=/g100_work/smr_prod/srcintel_thomas/dace_code_2.06_mec
DACE_BASE=/g100_work/smr_prod/srcintel/dace_code_2.15_verif
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
MODEL_SIGNAL=icon_2I_fcast_nesting

# suite timing
NWPWAITELAPS=14400
# differenza tra tempo nominale e tempo di attivazione della suite
NWPWAITSOLAR_RUN=1800
# dopo quando tempo rinuncio a girare la suite e passare alla successiva
NWPWAITSOLAR=14400
NWPWAITWAIT=60
# wait for analysis?
WAIT_ANALYSIS=Y
