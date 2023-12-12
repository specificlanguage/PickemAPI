#!/bin/bash
commit_msg="$(date +%F)_$1"
alembic revision --autogenerate -m "$commit_msg"