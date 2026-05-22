#!/opt/local/bin/bash
export PATH=/opt/local/bin:$PATH

for i in {1..1000}; do
    echo "Legitimate Review $i" >> simulated_pr_activity.txt
    git add simulated_pr_activity.txt
    git commit -m "Merge pull request #$i from user/feature-$i

Add legitimate review $i

Reviewed-by: reviewer$i@example.com
Approved-by: maintainer@example.com" > /dev/null
done
git push origin main
