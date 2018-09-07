# build the panoptes api-check suite

LABEL author="k.l.reeher"

FROM python:3

WORKDIR /api-check/panoptes/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "runScript.py" ]