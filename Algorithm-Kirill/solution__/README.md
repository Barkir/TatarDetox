### Инструкция по использованию нашего решения

1. Мы скачивам тестовый файл `test_inputs.tsv`

2. После этого переводим наш дата-сет на английский

```
python3 translate_to_english.py <from> <to>
```
> **from**, **to** задают диапазон строк, который будет обработан моделью. Чтобы указать прочтение до конца файла - нужно указать **_очень большое число_**.

3. Ответ приходит в виде json, поэтому мы его парсим для нужного формата для baseline_mt0

```
python3 json_to_fmt.py
```

4. Теперь запускаем baseline_mt0

```
python3 main.py --input_path baseline.tsv --output_path output_test.tsv --batch_size 32
```

- Получили файл output_test.tsv, который имеет хедеры

`toxic_text lang non_toxic_text`


5. После этого мы убираем поле `toxic_text` из этого результата и ставим в формат для перевода дальше на татарский.

```
python3 parse_clean_text.py output_test.tsv
```


6. Теперь переводим наш текст с английского на татарский

```
python3 translate_to_tatar.py <from> <to>
```
> **from**, **to** работает так же как и в _translate_to_english.py_


7. Теперь пропарсим текст который получили после перевода.

```
json_to_answer.py
```
8. На выходе получаем `output.tsv` - итоговую БД с детоксифицированным текстом.
