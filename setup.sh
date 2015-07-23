#!/bin/bash

rm -rf vendor
mkdir vendor
cd vendor
git clone git@github.com:zestyping/openpixelcontrol.git
cd openpixelcontrol
make