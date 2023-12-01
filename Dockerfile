# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y software-properties-common postgresql postgresql-contrib
