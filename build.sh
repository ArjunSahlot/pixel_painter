#!/bin/bash

download_link=https://github.com/ArjunSahlot/pixel_painter/archive/main.zip
temporary_dir=$(mktemp -d) \
&& curl -LO $download_link \
&& unzip -d $temporary_dir main.zip \
&& rm -rf main.zip \
&& mv $temporary_dir/pixel_painter-main $1/pixel_painter \
&& rm -rf $temporary_dir
echo -e "[0;32mSuccessfully downloaded to $1/pixel_painter[0m"
