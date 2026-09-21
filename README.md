# Text Expander

A small, local, dependency-free CLI for storing reusable text snippets and expanding safe `{{variables}}` templates. It is designed for signatures, replies, release text, commands you want to *display* (not execute), support responses, and other repeated writing.

> English documentation first. [العربية](#العربية)

## Why this exists
Repeated text is easy to mistype and hard to keep consistent. Text Expander keeps a named snippet library on your machine and lets you render templates deterministically without accounts, cloud services, telemetry, or runtime dependencies.

## Features

- Add, replace, list, inspect, expand, and delete named snippets.
- Template variables such as `{{name}}` supplied with `--var name=value`.
- Built-ins: `{{date}}`, `{{time}}`, and `{{datetime}}` using local time.
- Strict missing-variable validation by default; optional `--allow-missing`.
- Persistent versioned JSON store with atomic replacement writes.
- JSON output for `list`, `show`, and `expand` automation use cases.
- Import/export with conflict and overwrite protection.
- Configurable store via `--store` or `TEXT_EXPANDER_STORE`.
- Cross-platform Python 3.10+; standard library only at runtime.
- Snippet text is substituted literally and is never executed as code or a shell command.

## Requirements
Python 3.10 or newer.

## Installation

```bash
git clone https://github.com/rad03i2/text-expander.git
cd text-expander
python -m pip install .
text-expander --version
```

For development:

```bash
python -m pip install -e .
```

## Usage

```bash
# Add plain text
text-expander add signature "Regards,\nRadwan"

# Add a template
text-expander add welcome "Hello {{name}} — today is {{date}}" --description "Greeting"

# Expand it
text-expander expand welcome --var name=Ali

# Inspect required variables
text-expander show welcome --json

# List snippets
text-expander list
text-expander list --json

# Read multiline content from a UTF-8 file
text-expander add reply --file reply.txt

# Replace an existing snippet explicitly
text-expander add welcome "Hi {{name}}" --overwrite

# Backup and restore
text-expander export backup.json
text-expander import backup.json

# Delete
text-expander delete welcome
```

Values may contain `=`; parsing splits only on the first equals sign. Multiple variables use repeated `--var` options.

## Configuration
By default, data is stored under `%APPDATA%/TextExpander/snippets.json` on Windows and `$XDG_DATA_HOME/text-expander/snippets.json` (or `~/.local/share/text-expander/snippets.json`) elsewhere.

Override it per command:

```bash
text-expander --store ./private/snippets.json list
```

Or set `TEXT_EXPANDER_STORE` to a file path. No `.env` file is required.

## Import format
The portable format is versioned JSON:

```json
{
  "version": 1,
  "snippets": [
    {"name": "hello", "text": "Hello {{name}}", "description": "Greeting"}
  ]
}
```

See `examples/snippets.json` for a ready-to-import safe sample.

## Project structure

```text
src/text_expander/core.py   storage, validation, templates
src/text_expander/cli.py    command-line interface
tests/                      unit + CLI integration tests
examples/snippets.json      import example
.github/workflows/ci.yml    cross-platform CI
```

## Testing

```bash
python -m pip install .
python -m unittest discover -s tests -v
```

CI runs the suite and installed CLI on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13.

## Preview / screenshots
This is intentionally a terminal application. A useful repository screenshot can show `text-expander list`, followed by an `expand` command and its rendered output. No graphical interface is claimed.

## Security & privacy
All runtime data remains local. There is no telemetry or network call in the application. The JSON store is **not encrypted**: do not store passwords, API keys, tokens, or other secrets in it. Import only files you trust and review filesystem permissions for sensitive prose. See `SECURITY.md`.

## Limitations

- This release is a CLI, not a system-wide keyboard-hook application; it does not automatically replace abbreviations while typing in other apps.
- The store is plaintext JSON and is not a secret manager.
- Templates intentionally support variable substitution only—no expressions, loops, scripting, clipboard access, or command execution.
- Concurrent writers are not coordinated with a cross-process lock; atomic replacement protects against partial files, but callers should serialize writes.

## Optional roadmap
Future work may include an opt-in desktop tray/keyboard integration and explicit file locking. These are not current features.

## Contributing
See `CONTRIBUTING.md`. Keep changes focused, tested, local-first, and free of secrets.

## License
MIT — see `LICENSE`.

## Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية

## نظرة عامة
**Text Expander** أداة سطر أوامر محلية وخفيفة لحفظ النصوص المتكررة بأسماء واضحة ثم استخدامها كقوالب آمنة عبر متغيرات بالشكل `{{name}}`. تفيد للتواقيع والردود المتكررة ونصوص الإصدارات والقوالب الكتابية، من دون حساب أو خدمة سحابية أو تتبع.

## لماذا المشروع؟
إعادة كتابة النص نفسه تسبب أخطاء وعدم اتساق. يوفر المشروع مكتبة محلية بسيطة وقابلة للنسخ الاحتياطي، مع توسعة قوالب واضحة لا تنفذ النص كأوامر أو كود.

## المزايا

- إضافة النصوص وتعديلها الصريح وعرضها والبحث عنها بالاسم عبر القائمة وحذفها.
- متغيرات مثل `{{name}}` تمرر باستخدام `--var name=value`.
- متغيرات مدمجة للتاريخ والوقت: `{{date}}` و`{{time}}` و`{{datetime}}`.
- اكتشاف المتغيرات الناقصة افتراضيًا، مع `--allow-missing` عند الحاجة.
- تخزين JSON بإصدار محدد وكتابة استبدالية ذرية لتقليل خطر تلف الملف.
- مخرجات JSON لأوامر `list` و`show` و`expand`.
- استيراد وتصدير مع حماية من التعارض والاستبدال غير المقصود.
- يعمل على Python 3.10+ بلا مكتبات تشغيل خارجية.

## التثبيت

```bash
git clone https://github.com/rad03i2/text-expander.git
cd text-expander
python -m pip install .
text-expander --version
```

## الاستخدام

```bash
text-expander add greeting "مرحباً {{name}}، التاريخ {{date}}"
text-expander expand greeting --var name=علي
text-expander list
text-expander show greeting --json
text-expander export backup.json
text-expander import backup.json
text-expander delete greeting
```

للنص متعدد الأسطر يمكن استخدام `--file`. وللاستبدال المتعمد لنص موجود استخدم `--overwrite`.

## الإعداد
على Windows يكون المسار الافتراضي داخل `%APPDATA%/TextExpander/snippets.json`، وعلى الأنظمة الأخرى داخل `$XDG_DATA_HOME/text-expander/snippets.json` أو `~/.local/share/text-expander/snippets.json`. يمكن تغييره عبر `--store` أو متغير البيئة `TEXT_EXPANDER_STORE`. لا يحتاج المشروع إلى `.env`.

## بنية المشروع
المحرك والتحقق والتخزين في `src/text_expander/core.py`، وواجهة الأوامر في `src/text_expander/cli.py`، والاختبارات في `tests/`، والمثال في `examples/snippets.json`، وCI في `.github/workflows/ci.yml`.

## الاختبارات

```bash
python -m pip install .
python -m unittest discover -s tests -v
```

تم إعداد CI لاختبار المشروع على Linux وWindows وmacOS مع Python 3.10 و3.12 و3.13.

## المعاينة
المشروع أداة طرفية عمدًا؛ يمكن لصورة المعاينة أن تعرض أمر `list` ثم أمر `expand` والنتيجة. لا يدعي المشروع وجود واجهة رسومية.

## الأمان والخصوصية
لا يرسل البرنامج النصوص إلى الإنترنت ولا يحتوي Telemetry. التخزين JSON نصي **غير مشفر**، لذلك لا تستخدمه لحفظ كلمات المرور أو المفاتيح أو Tokens. توسعة القوالب استبدال نصي فقط ولا تنفذ أوامر. راجع `SECURITY.md`.

## القيود
الإصدار الحالي ليس برنامج اختصارات يعمل تلقائيًا أثناء الكتابة داخل التطبيقات الأخرى، ولا يراقب لوحة المفاتيح عالميًا. لا يوجد تشفير للتخزين أو لغة قوالب برمجية، ولا توجد آلية قفل بين عدة عمليات كتابة متزامنة.

## تطوير اختياري لاحق
يمكن مستقبلًا إضافة تكامل اختياري مع شريط النظام واختصارات لوحة المفاتيح وقفل ملفات بين العمليات. هذه ليست ميزات موجودة حاليًا.

## المساهمة
راجع `CONTRIBUTING.md`. يجب أن تكون التغييرات محددة ومختبرة وألا تحتوي بيانات خاصة أو أسرارًا.

## الترخيص
MIT، والتفاصيل في `LICENSE`.

## المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
