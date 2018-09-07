# build the panoptes api-check suite
FROM python:3
LABEL author="k.l.reeher"
WORKDIR /api-check/panoptes/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "runScript.py" ]