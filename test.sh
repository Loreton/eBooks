#!/bin/bash
#
alias chiamabar="bar_01"

function caller() {
    echo "---"
    echo "      function:  $(basename ${BASH_SOURCE[1]})->${FUNCNAME[1]}"
    echo "      called by: $(basename ${BASH_SOURCE[2]})->${FUNCNAME[2]}"
    echo "---"
}



function foo_01() {
    caller
    # echo "---"
    # echo "      function:  $(basename ${BASH_SOURCE[0]})->${FUNCNAME[0]}"
    # echo "      called by: $(basename ${BASH_SOURCE[1]})->${FUNCNAME[1]}"
    # echo "---"
}

function bar_01() {
    foo_01
}

