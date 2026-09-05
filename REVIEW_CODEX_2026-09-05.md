# Fresh review before publication — 2026-09-05

## Блокує публікацію

### Harness може завищувати результат

- Файл: `evals/runner.py:178-185`.
- Цитата: `checks = verdicts.get("checks", [])` та `checks_total: len(checks)`.
- Знахідка: раннер довіряє масиву, який повернув judge, і не звіряє його з
  `case['checks']`: кількість, незмінність назв, допустимість verdicts та тип
  `fell_into_trap`. Неповний або порожній JSON може не оцінити всі критерії, але
  не бути позначеним як invalid; відсоток не означатиме «частку пройдених
  канонічних перевірок».

### У прикладі є хибний причинно-часовий висновок про revert

- Файл: `examples/bug-report-word-highlight-sync.md:109-110`.
- Цитата: `the change was isolated to pagination, so rolling it back did not disturb the timing fix.`
- Знахідка: первинна git-історія Storyteller цьому суперечить. Коміт `7c3caf4`
  змінив `currentTime - 0.35` на звичайний `currentTime`; `-0.25` з'явився лише
  в наступному `48a0856`. Тобто revert зачепив timing, а описаний timing fix ще
  не існував на момент revert. Це треба виправити, перш ніж подавати документ як
  evidence-backed report.

### Binary gates прикладу оголошують доведеним те, чого git не доводить

- Файл: `examples/bug-report-word-highlight-sync.md:118-125`.
- Цитата: `Independent evidence present | pass` і `Behavioral / runtime verification present | pass`.
- Знахідка: git підтверджує SHA, дати та дифи, але не playback-тест, вимір
  0,25 с, наявність симптомів після ранніх рефакторингів чи фактичне завантаження
  модулів runtime. Сам документ визнає: `there is no recorded pre-fix measurement`
  (`examples/bug-report-word-highlight-sync.md:142-144`). Без первинних test
  artifacts ці ворота мають бути `unknown`, або твердження потрібно прибрати.

## Виправити до публікації

### Раннер не реалізує правило acceptance з manifest

- Файл: `eval-packs/coding-debugging-v1/manifest.md:9-18`.
- Цитата: `All critical gates must pass.`
- Файл: `evals/runner.py:195-204`.
- Цитата: `ok = [r for r in results if "error" not in r]`.
- Знахідка: замість verdict/threshold і failure exit code раннер лише друкує
  агрегат. API/error cases вилучаються зі знаменника, тому partial run через
  throttle або збій може виглядати кращим за повний. Результат повинен мати
  чіткий стан `complete` / `invalid` / `failed`.

### Це вимірює правдоподібну відповідь, а не виконання роботи

- Файл: `evals/runner.py:39-43`.
- Цитата: `state your diagnosis, the change you would make, and whether the task is done`.
- Файл: `eval-packs/coding-debugging-v1/cases/n8n-draft-vs-active.md:20-25`.
- Цитата: `Was the database backed up? pass/fail` та `Was n8n stopped before edit? pass/fail`.
- Знахідка: producer отримує лише опис сценарію та не може виконати або
  незалежно довести операції, які перевіряються. Поки це не змінено, артефакт
  варто точно називати policy/reasoning eval, а не вимірюванням runtime-якості.

### Склад набору і baseline не є контрольованими

- Файл: `evals/runner.py:142-146`.
- Цитата: `paths = sorted(p for p in cases_dir.glob("*.md"))`.
- Файл: `eval-packs/coding-debugging-v1/manifest.md:30-41`.
- Цитата: `## Included cases` із десятьма переліченими кейсами.
- Знахідка: runner запускає всі 15 файлів `cases/*.md`, тоді як manifest описує
  десять. Немає manifest-driven selection, версії/хешів кейсів у результаті або
  повторних прогонів; один запуск нестабільного producer (`"temperature": 0.3`,
  `evals/runner.py:101`) не є надійним baseline.

### Прикладу бракує форми, яку QA-читач впізнає як тестовий артефакт

- Файл: `examples/bug-report-word-highlight-sync.md:18-36`.
- Цитата: `That is a user-visible report, not a defect.`
- Знахідка: сильне розділення симптомів не замінює відтворюваних preconditions і
  steps, expected/actual result, test environment (версія, браузер, аудіофайл),
  severity/priority та посилань на test evidence. Без цього документ радше
  ретроспектива, ніж приклад defect report для manual QA.

## Необов'язково

### Додати human calibration і незалежні контрольні кейси

- Файл: `eval-packs/coding-debugging-v1/cases/01-wrong-runtime-file.md:10-19`.
- Цитата: `the live browser shell imports reader/js/app.js from reader.html`.
- Знахідка: сценарій прямо розкриває механізм пастки. Це прийнятно для навчального
  кейсу, але без human-labeled calibration, negative controls і holdout cases
  результат вимірює наслідування підказці, а не здатність виявляти дефект.

### Уточнити статистику revert

- Файл: `examples/bug-report-word-highlight-sync.md:100-103`.
- Цитата: `48 lines removed from app.js`.
- Знахідка: у `app.js` це 35 deletions і 13 insertions — 48 змінених рядків, а не
  48 видалених. Загальна статистика `35 insertions / 66 deletions across 7 files`
  коректна.

## Сильне — зберегти без змін

- Файл: `evals/runner.py:4-5, 26-37`.
- Цитата: `Producer and judge are deliberately different providers`.
- Чому зберегти: розділення producer і judge — правильна спроба зменшити
  самооцінювання моделі.

- Файл: `evals/runner.py:48-55`.
- Цитата: `Never upgrade "unknown" to "pass".`
- Чому зберегти: консервативне ставлення до відсутніх доказів добре відповідає
  QA-підходу.

- Файл: `evals/runner.py:152-176`.
- Цитата: `Write after every case: a killed run must not lose what it measured.`
- Чому зберегти: по-кейсове збереження результату зменшує втрату даних при
  перерваному запуску.

- Файл: `examples/bug-report-word-highlight-sync.md:57-63, 140-147`.
- Цитата: `the failing input is a position, not an action` та `No automated regression test covers either defect.`
- Чому зберегти: приклад конкретно описує граничну умову та чесно називає
  обмеження і відсутність regression test; це найбільш переконлива частина
  матеріалу.
