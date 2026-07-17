FROM python:3.12-slim
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates git cmake ninja-build build-essential libssl-dev \
    && git clone --depth 1 --branch 0.16.0 https://github.com/open-quantum-safe/liboqs.git /tmp/liboqs \
    && cmake -S /tmp/liboqs -B /tmp/liboqs/build -GNinja -DBUILD_SHARED_LIBS=ON -DOQS_BUILD_ONLY_LIB=ON \
    && cmake --build /tmp/liboqs/build \
    && cmake --install /tmp/liboqs/build \
    && rm -rf /tmp/liboqs /var/lib/apt/lists/*
ENV OQS_INSTALL_PATH=/usr/local
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
