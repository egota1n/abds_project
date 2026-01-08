#### Загрузка тестового датасета в формате csv

Для загрузки [тестовых данных](https://drive.google.com/file/d/1dsVSfj4mnTCz_i4ZRRxFpIAEwqv26wNh/view?usp=sharing) в формате csv необходимо поместить в эту директорию файл event.csv

После чего отдельно запустить сервис csv_loader командой

```bash
docker compose build csv_loader
docker compose run csv_loader
```