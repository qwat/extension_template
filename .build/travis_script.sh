#!/usr/bin/env bash

set -e

cd $TRAVIS_BUILD_DIR

echo `pwd`
git clone --recurse-submodules https://github.com/qwat/qwat-data-model.git

wget -q -O qwat_dump.backup https://github.com/qwat/qwat-data-sample/raw/master/qwat_v1.2.1_data_and_structure_sample.backup

export SRID=21781
export QWAT_DIR="$TRAVIS_BUILD_DIR/qwat-data-model"
export VERSION=$(sed 'r' "$QWAT_DIR/system/CURRENT_VERSION.txt")

# Create a PostgreSQL service file and export the PGSERVICEFILE environment variable
PGSERVICEFILE="/tmp/pg_service.conf"
cat > $PGSERVICEFILE << EOF
[qwat_prod]
host=localhost
dbname=qwat_prod
user=postgres

[qwat_test]
host=localhost
dbname=qwat_test
user=postgres

[qwat_comp]
host=localhost
dbname=qwat_comp
user=postgres
EOF
export PGSERVICEFILE

DELTA_DIRS="$QWAT_DIR/update/delta/"

# Restore the 1.2.1 dump in the prod database
pum restore -p qwat_prod qwat_dump.backup

# Set the baseline for the prod database
pum baseline -p qwat_prod -t qwat_sys.info -d $DELTA_DIRS -b 1.2.1

# Run init_qwat.sh to create the last version of qwat db used as the comp database
printf "travis_fold:start:init-qwat\nInitialize database"
$QWAT_DIR/init_qwat.sh -p qwat_comp -s $SRID -r -n
echo "travis_fold:end:init-qwat"

# Run test_and_upgrade
printf "travis_fold:start:test-and-upgrade\nRun test and upgrade"
yes | pum test-and-upgrade -pp qwat_prod -pt qwat_test -pc qwat_comp -t qwat_sys.info -d $DELTA_DIRS -f /tmp/qwat_dump -i views rules
echo "travis_fold:end:test-and-upgrade"

# Run a last check between qwat_prod and qwat_comp
pum check -p1 qwat_prod -p2 qwat_comp -i views rules


# Extend qwat_prod with EXTENSION
printf "travis_fold:start:init-sire\nExtend database with EXTENSION"
$TRAVIS_BUILD_DIR/extension/init.sh -p qwat_prod -s $SRID
echo "travis_fold:end:init-extension"

# Set the baseline for the comp database
pum baseline -p qwat_comp -t qwat_sys.info -d $DELTA_DIRS -b $VERSION

# Run upgrade with EXTENSION as an extra delta dir
DELTA_DIRS="$DELTA_DIRS $TRAVIS_BUILD_DIR/extension/delta"
printf "travis_fold:start:upgrade\nRun upgrade"
pum upgrade -p qwat_prod -t qwat_sys.info -d $DELTA_DIRS
echo "travis_fold:end:upgrade"
