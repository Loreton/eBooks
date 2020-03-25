#!/bin/bash
branch=$(git status | grep "On branch" | cut -d' ' -f3)
comment=$*
# echo "$comment"
if [ -z "$comment" ]; then
    echo "please enter a comment for this commit"
    echo
    exit 1
fi
git add --all
git commit --all --message '"'$comment'"'
# git push gitHub $branch
# git push gitLab $branch
# git push gitBucket $branch