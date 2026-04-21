REGISTRY_IMAGE := registry.gitlab.com/metaforges/greek-exam
BACKEND_IMAGE := $(REGISTRY_IMAGE):backend-v0.1.0
FRONTEND_IMAGE := $(REGISTRY_IMAGE):frontend-v0.1.0
DOCKER ?= docker
PLATFORM ?= linux/amd64
VITE_API_URL ?=

.PHONY: backend frontend

backend:
	$(DOCKER) build --platform $(PLATFORM) -t $(BACKEND_IMAGE) ./backend
	$(DOCKER) push $(BACKEND_IMAGE)

frontend:
	$(DOCKER) build --platform $(PLATFORM) --build-arg VITE_API_URL=$(VITE_API_URL) -t $(FRONTEND_IMAGE) ./frontend
	$(DOCKER) push $(FRONTEND_IMAGE)
