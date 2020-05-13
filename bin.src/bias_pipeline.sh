REPO_DIR="$CI_CPP_GEN3_DIR"/DATA/
OUT_DIR="$REPO_DIR"/ci_cpp_bias/


echo "REPO_DIR: $REPO_DIR"
echo "OUT_DIR:  $OUT_DIR"
pipetask run -j 4 \
    -d "detector=0 AND exposure IN (2020012800007,2020012800008,2020012800009,2020012800010)" \
    -b "$REPO_DIR"/butler.yaml \
    -i calib,calib/lsst,raw/latiss \
    -o ci_cpp_bias \
    -p $OBS_LSST_DIR/pipelines/latiss/cpBias.yaml \
    --register-dataset-types

"$CP_PIPE_DIR"/bin/blessCalibration.py $OUT_DIR ci_cpp_bias  calib/v00 -b 1950-01-01 -e 2050-01-01 bias
