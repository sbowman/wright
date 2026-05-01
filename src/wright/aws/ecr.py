import sh

# TODO: https://github.com/boto/boto3

def create_repository(region: str, repository_name: str):
    """
    Create a repository in AWS Elastic Container Registry if it doesn't exist.
    The repository name should not include the hostname bit of the repository.
    For example, if your image tag is something like:

        97829rt74e748ew87.dkr.ecr.us-east-2.amazonaws.com/myapp/myservice:3.7.23

    Then the repository name should be `myapp/myservice`.
    """
    try:
        sh.aws(["ecr", "create-repository", "--repository-name", repository_name, "--region", region])


        # TODO: add lifecycle policy
    except sh.ErrorReturnCode as e:
        if e.stdout.decode().strip() == "[]":
            return False


# aws ecr put-lifecycle-policy \
#     --repository-name division/blah/bob \
#     --lifecycle-policy-text file://policy.json \
#     --region us-east-1


def describe_images(region: str, repository_name: str):
    """
    List the versions of the given image that are available, along with when
    they were pushed.
    """
    pass


# aws ecr describe-images --repository-name conduit/flynn --region us-east-2
# {
#     "imageDetails": [
#         {
#             "registryId": "982534376887",
#             "repositoryName": "conduit/flynn",
#             "imageDigest": "sha256:aa293b8f2323c1bce61bd1060a92abc4472975f8d7e21cab5bf495fa62e546b8",
#             "imageTags": [
#                 "0.6.0"
#             ],
#             "imageSizeInBytes": 10983130,
#             "imagePushedAt": "2026-02-20T15:13:33.998000-07:00",
#             "imageManifestMediaType": "application/vnd.docker.distribution.manifest.v2+json",
#             "artifactMediaType": "application/vnd.docker.container.image.v1+json"
#         }
#     ]
# }


def authenticate_ecr(region: str, username: str, host: str):
    sh.Command(f"aws ecr get-login-password --region {region} | docker login --username {username} --password-stdin {host}")
