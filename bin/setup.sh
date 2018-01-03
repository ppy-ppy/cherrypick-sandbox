#!/bin/bash

configExec() {
    exp="$1"
    iType="$2"
    iCount="$3"

    outputDir="$exp-$iType-$iCount-results"
    experiment="final-$exp-template"
    root=".."

    ########################################
    # Generate the benchmark
    ########################################
    local expName=$(./gen.sh -b $experiment -c $root -n $iCount)
    expName=$(echo $expName | xargs)

    if [ -z $expName ]; then
        echo "No such experiment ($experiment) was found."
        exit 1
    fi

    if [ $? -ne 0 ]; then
        echo "Error: could not create experiment for $outputDir";
        exit 1
    fi

    ########################################
    # Initialize the parameter used by the cb script
    ########################################
    expSpec="$expName: ($exp, $iType, $iCount)"
    echo "Running $expSpec"

    # Build the benchmark parameters
    params="placement-group=false"
    params="$params,instance-type=$iType"

    paramsQ="--params=$params"
    expQ="--benchmark=$expName"
    cloudQ="--cloud=sahara"
    noExecQ="--no-execute"
    setupQ="--setup"
    teardownQ="--teardown"
    verboseQ="-vvvv"

    cbBaseInput=$(printf "%s\0%s\0%s\0" $expQ $cloudQ $verboseQ)
    cbExecute=$(printf "%s\0" $cbBaseInput $paramsQ)

    cbNoExecute=$(printf "%s\0" $cbBaseInput $noExecQ)
    cbSetup=$(printf "%s\0" $cbNoExecute $setupQ)
    cbTeardown=$(printf "%s\0" $cbNoExecute $teardownQ)

    ########################################
    # Run the experiment
    ########################################

    # Setup
    echo "> Setting up: $expSpec"
    printf "%s\0" $setupQ $noExecQ $paramsQ $expQ $cloudQ $verboseQ | \
        xargs -0 bash -c './cb "$@"' --
    sleep 1
}

export -f configExec

parallelization=${1:-no-value}
exp=${2:-"terasort"}
iType=${3:-"m1.small"}
iCount=${4:-"4"}

printConfigs() {
    echo -n
    printf "%s\0%s\0%s\0%s\0" $exp $iType $iCount
}

usage() {
    echo -n "run.sh [PARALLELIZATION LEVEL] [Experiment] [InstanceType] [Machine Count]

Please add the configs that you want to run to the printConfigs
function inside the script.  The syntax is:

> configFor \"Experiment\" \"InstanceType\" \"Machine Count\" \"Disk Type\"

1) Experiment: any one of: tpcds, tpch, tera, spark, kmeans
2) Instance type: any of the instance types in Amazon
3) Instance count: number of instances in the cluster

By default the disks are set to be 2x250GB of gp2 type per instance.
Feel free to change that within this file.
"
}

########################################
# PARALLELIZATION
########################################

if [[ "$parallelization" == "no-value" ]]; then
    usage
else
    printConfigs | xargs -0 -n 4 -P $parallelization bash -c 'configExec "$@"' --
fi

