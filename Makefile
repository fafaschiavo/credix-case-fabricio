start:
	make stop; docker compose up --build

stop:
	docker compose down -v

build:
	make clear ; docker compose --file docker-compose-build.yml up --build

clear:
	docker stop credix-case-frontend-build ; docker rm credix-case-frontend-build ; make stop

push-image:
	@AWS_ACCOUNT_ID=$$(aws sts get-caller-identity --query Account --output text); \
	echo "Using AWS_ACCOUNT_ID=$$AWS_ACCOUNT_ID"; \
	docker build -t credix-case-fabricio-django-api ./back; \
	docker tag credix-case-fabricio-django-api:latest $$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/credix-case-fabricio-django-api:latest; \
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com; \
	docker push $$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/credix-case-fabricio-django-api:latest

prepare-infra:
	cd "terraform" && terraform init ; terraform destroy -auto-approve ; terraform apply -auto-approve