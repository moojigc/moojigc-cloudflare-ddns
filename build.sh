set -e

git add .
git commit -m "$1"

sudo docker build . -t dr.chimid.rocks/cloudflare-ddns:$(git rev-parse --short HEAD)

git rev-parse --short HEAD