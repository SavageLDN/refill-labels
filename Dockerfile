# Minimal image to publish as a package (GHCR) for activity/badges
FROM alpine:3.18
LABEL org.opencontainers.image.title="refill-labels"
LABEL org.opencontainers.image.description="Refill label generator - CI artifact image"
CMD ["/bin/sh","-c","echo Refill Labels image built"]
