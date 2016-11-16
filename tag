#!/bin/sh

if ! [ $# -eq 2 ]; then
  echo Must supply tag name and description
  exit 1
fi

tag=$1
description=$2

if ! [ -z "$(git status --porcelain)" ]; then
  echo 'Untracked changes!'; echo; git status
  exit 2
fi

sqitch tag $tag -n "sqitch tag $tag: $description" || exit 9
git commit -am "sqitch tag $tag: $description" || exit 9
git tag -f $tag || exit 9
git fetch . $tag:prod || exit 9

echo "If everything looks good:"
echo "git push --all"

# vi: expandtab ts=2 sw=2
