FROM python:3.9-buster

USER root

# Install WeasyPrint dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libffi-dev \
    libpango1.0-dev \
    libpango-1.0-0 \
    libharfbuzz0b \
    libharfbuzz-dev \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libgirepository-1.0-1 \
    gir1.2-gtk-3.0 \
    libgirepository1.0-dev \
    libglib2.0-dev \
    libcairo2-dev \
    libcairo-gobject2 \
    libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
RUN mkdir /opt/app-root && chmod 755 /opt/app-root
WORKDIR /opt/app-root

# Install the requirements
COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install .

USER 1001

# Set Python path
ENV PYTHONPATH=/opt/app-root/src

# Set GTK3 path for WeasyPrint
ENV GTK_PATH=/usr/lib/x86_64-linux-gnu
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu

ENTRYPOINT ["bash", "docker-entrypoint.sh"]
