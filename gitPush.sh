#!/bin/bash
branch=$(git status | grep "On branch" | cut -d' ' -f3)
comment=$*
# echo "$comment"
if [ -z "$comment" ]; then
    echo "please enter a comment for this commit"
    echo
    exit 1
fi

echo git add --all
git add --all
echo

echo git commit --all --message "$comment"
git commit --all --message "$comment"
echo

echo git push gitHub $branch
git push gitHub $branch
echo

echo git push gitLab $branch
git push gitLab $branch
echo

echo git push gitBucket $branch
git push gitBucket $branch
echo