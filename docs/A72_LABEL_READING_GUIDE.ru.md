# A72 pedagogy — как читать словарные пометы (m./f./n./mfn., P./A./U., c., V./N./M./S.: вычисленный путеводитель)

_Created: 13-10-2026 · Last updated: 13-10-2026_

Сгенерировано [`scripts/build_abbrev_label_guide.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build_abbrev_label_guide.py) (handoff [H6465](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6465-OxAlpha_csl-atlas_a72-label-reading-student-guide_11.10.26.md)) из ценза грамматических сокращений [data/abbrev/abbrev_census.json](../data/abbrev/abbrev_census.json) (H6409, снапшот от 2026-10-10T19:00:00.879Z). **Каждая строка — это вычисленная строка ценза, а не пересказ по памяти**: расшифровка приводится дословно из слоя легенд, а помета, которой нет в цензе, помечается «нет в цензе» и не толкуется. Машинный двойник таблицы — [data/abbrev/label_guide_rows.tsv](../data/abbrev/label_guide_rows.tsv).

## Зачем это студенту

В цифровизированном каноне CSDL 34765 разных сокращений; у 4752 из них есть расшифровка в слоях легенд, и **448 из них многозначны** (≥2 разных расшифровок в разных словарях — вычислено, не по памяти). Одна и та же помета в Мономье (MW) и в Апте (AP90) может означать разное: ниже — как читать её не гадая.

## Правило чтения (3 шага)

1. **Определи словарь.** Помета живёт внутри конкретного словаря: сначала посмотри, чья статья перед тобой (MW, PWG, AP90…), потом читай пометы этого словаря.
2. **Не угадывай по букве.** У одних и тех же строк ниже — от 1 до 12 разных расшифровок (столбец «смыслов» посчитан по легендам ценза).
3. **Если пометы нет в таблице — считай, что ты её не знаешь.** Мы не пересказываем по памяти: «нет в цензе» значит «не вычислено».

## Родовые пометы

Одна буква — но словари пишут её по-разному (латынь, французский, немецкий).

### `m.` — Мужской род

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **5**; строк легенд дословно: 8. Встречается в статьях словарей: ae,ap,ap90,ben,bhs,bur,cae,gra,lan,md,mw,pw,pwg,pwkvn,stc,wil.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Masculine` | AE |
| `Masculine.` | AP, AP90, LRV |
| `masculine.` | BHS, CAE, MD |
| `masculin` | BUR |
| `meaning.` | CAE |
| `masculinum` | GRA |
| `masculine gender` | MW |
| `masculin.` | STC |

### `f.` — Женский род

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **6**; строк легенд дословно: 10. Встречается в статьях словарей: ae,ap,ap90,ben,bhs,bur,cae,gra,lan,md,mw,pw,pwg,pwkvn,stc,wil.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Feminine` | AE |
| `Feminine.` | AP, AP90 |
| `feminine; following.` | BHS |
| `féminin` | BUR |
| `feminine.` | CAE |
| `femininum` | GRA |
| `Feminine (of adjectives).` | LRV |
| `feminine; also = for.` | MD |
| `feminine` | MW |
| `féminin.` | STC |

### `n.` — Средний род

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **6**; строк легенд дословно: 8. Встречается в статьях словарей: ae,ap,ap90,ben,bhs,bur,cae,gra,lan,md,mw,pw,pwg,pwkvn,stc,wil.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Neuter` | AE |
| `Neuter.` | AP, AP90, LRV |
| `nominative; name.` | BHS |
| `neutre` | BUR |
| `neuter.` | CAE, MD |
| `neutrum` | GRA |
| `neuter gender` | MW |
| `nom.` | STC |

### `mfn.` — Все три рода / прилагательное

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **1**; строк легенд дословно: 1. Встречается в статьях словарей: mw,wil.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `masculine, feminine and neuter; or = adjective` | MW |

## Залог/пада: P., A., U.

Большие буквы — грамматика глагола: парасмайпада, атманепада, убхаяпада.

### `P.` — Парасмайпада (актив)

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **11**; строк легенд дословно: 24. Встречается в статьях словарей: ap,ap90,bhs,bur,cae,gra,md,mw,pw.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Parasmaipada.` | AP, AP90, MD |
| `Pāṇini's Aṣṭādhyāyī.` | AP90 |
| `1) Parasmaipadum. 2) P�taliputra (ed. H. Brockhaus. Lipsiae 1835.)` | BOP |
| `1) Parasmaipadum. 2) Påtaliputra (ed. H. Brockhaus. Lipsiae 1835.)` | BOP |
| `parfait` | BUR |
| `Passive.` | CAE |
| `Participium` | GRA |
| `Pitṛ.` | INM |
| `Parasmai-pada` | MW |
| `Parasmai-pada.` | MW72 |
| `PĀṆINI. (vol. 1)` | PW |
| `PĀṆINI'S acht Bücher grammatischer Regeln (GILD. Bibl. 244).` | PWG |
| `Parasmaipada.` | AP, AP90, MD |
| `Pāṇini's Aṣṭādhyāyī.` | AP90 |
| `1) Parasmaipadum. 2) P�taliputra (ed. H. Brockhaus. Lipsiae 1835.)` | BOP |
| `1) Parasmaipadum. 2) Påtaliputra (ed. H. Brockhaus. Lipsiae 1835.)` | BOP |
| `parfait` | BUR |
| `Passive.` | CAE |
| `Participium` | GRA |
| `Pitṛ.` | INM |
| `Parasmai-pada` | MW |
| `Parasmai-pada.` | MW72 |
| `PĀṆINI. (vol. 1)` | PW |
| `PĀṆINI'S acht Bücher grammatischer Regeln (GILD. Bibl. 244).` | PWG |

### `A.` — Атманепада (медиум)

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **8**; строк легенд дословно: 10. Встречается в статьях словарей: ae,ap90,bhs,bur,cae,gra,pw,pwg,pwkvn.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Ātmanepada` | AE |
| `Ātmanepada.` | AP90 |
| `1) Atman�padum. 2) Arg'uni reditus ex Indri coelo. (*)` | BOP |
| `1) Atmanêpadum. 2) Arg'uni reditus ex Indri coelo. (*)` | BOP |
| `adjectif` | BUR |
| `Active.` | CAE |
| `Accusativ` | GRA |
| `Aśvin.` | INM |
| `Active` | MW |
| `Ātmane-pada ; the long mark over the A. has been omitted for convenience in printing.` | MW72 |

### `U.` — Оба пады

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **5**; строк легенд дословно: 5. Встречается в статьях словарей: ap,ap90,bhs,md,pw,pwg.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Ubhayapada (Parasmai and Atmane).` | AP |
| `Ubhayapada (Parasmai. and Ātmane.)` | AP90 |
| `Uttararāmacarita.` | AP90 |
| `Uraga.` | INM |
| `Upaniṣad.` | MD |

## Каузатив, падеж и класс глагола

Малые буквы, где самое опасное — перепутать грамматику с падежом.

### `c.` — Каузатив / падеж

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **4**; строк легенд дословно: 5. Встречается в статьях словарей: ae,ben,bhs,bur,gra,mw,pw,pwg.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Causal` | AE |
| `causatif` | BUR |
| `causativ` | GRA |
| `case` | MW |
| `case.` | MW72 |

### `D.` — Деноминатив / дезидератив / дат. / дэва

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **5**; строк легенд дословно: 5. Встречается в статьях словарей: ae,bhs,cae,gra,pw,pwg,pwkvn,wil.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Denominative` | AE |
| `Desiderative.` | CAE |
| `Dativ` | GRA |
| `Deva.` | INM |
| `SĀHITYADARPAṆA, ? [Cologne Addition]` | PWG |

### `med.` — Медиум (лат. medium)

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **1**; строк легенд дословно: 1. Встречается в статьях словарей: gra,md,mw,pw,pwg.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `medium` | GRA |

## Причастия: p., pp.

p. и pp. — пять-шесть разных смыслов, считанных из легенд.

### `p.` — Стр. / прич. / мн. ч. и др.

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **5**; строк легенд дословно: 5. Встречается в статьях словарей: ben,bhs,bur,cae,gra,md,mw,pwg,wil.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `parfait` | BUR |
| `possessive, v. pref.` | CAE |
| `plural` | GRA |
| `page and participle (cf. p.p.)` | MW |
| `page.` | MW72 |

### `pp.` — Причастие прошедшего времени

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **6**; строк легенд дословно: 6. Встречается в статьях словарей: bur,cae,gra,md,mw.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `participe passé` | BUR |
| `participle.` | CAE |
| `perge, perge‎` | GRA |
| `Past passive participle.` | LRV |
| `perfect passive participle.` | MD |
| `past participle` | MW |

## Однобуквенные титулы: V., N., M., S., R., K., H.

Главная ловушка: заглавная буква может быть названием произведения, а не грамматикой.

### `V.` — Веда / глагол / изд. Бардвана

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **7**; строк легенд дословно: 7. Встречается в статьях словарей: ae,bhs,gra,lan,md,mw,pw,pwg,pwkvn.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Vikramorvaśīyam (Bombay).` | AP90 |
| `Vôpadêvus grammaticus cujus radicum corpus, Kavikalpadruma inscriptum, edidit W. Carey in grammaticâ suâ. Westerg. est Westergardii liber Radices sanscritae inscriptus.` | BOP |
| `Vocativ` | GRA |
| `Burdwan edition.` | INM |
| `Vasu.` | INM |
| `Veda, Vedic.` | MD |
| `Verb.` | SHS |

### `P.` — Панини / парасмайпада

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **11**; строк легенд дословно: 24. Встречается в статьях словарей: ap,ap90,bhs,bur,cae,gra,md,mw,pw.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Parasmaipada.` | AP, AP90, MD |
| `Pāṇini's Aṣṭādhyāyī.` | AP90 |
| `1) Parasmaipadum. 2) P�taliputra (ed. H. Brockhaus. Lipsiae 1835.)` | BOP |
| `1) Parasmaipadum. 2) Påtaliputra (ed. H. Brockhaus. Lipsiae 1835.)` | BOP |
| `parfait` | BUR |
| `Passive.` | CAE |
| `Participium` | GRA |
| `Pitṛ.` | INM |
| `Parasmai-pada` | MW |
| `Parasmai-pada.` | MW72 |
| `PĀṆINI. (vol. 1)` | PW |
| `PĀṆINI'S acht Bücher grammatischer Regeln (GILD. Bibl. 244).` | PWG |
| `Parasmaipada.` | AP, AP90, MD |
| `Pāṇini's Aṣṭādhyāyī.` | AP90 |
| `1) Parasmaipadum. 2) P�taliputra (ed. H. Brockhaus. Lipsiae 1835.)` | BOP |
| `1) Parasmaipadum. 2) Påtaliputra (ed. H. Brockhaus. Lipsiae 1835.)` | BOP |
| `parfait` | BUR |
| `Passive.` | CAE |
| `Participium` | GRA |
| `Pitṛ.` | INM |
| `Parasmai-pada` | MW |
| `Parasmai-pada.` | MW72 |
| `PĀṆINI. (vol. 1)` | PW |
| `PĀṆINI'S acht Bücher grammatischer Regeln (GILD. Bibl. 244).` | PWG |

### `N.` — Имя / Найшадха / налa

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **10**; строк легенд дословно: 10. Встречается в статьях словарей: ap,ap90,bhs,bur,cae,gra,lan,md,mw,pw,pwg,pwkvn.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Name.` | AP, AP90, CAE, MW72 |
| `Naiṣadhacarita.` | AP90 |
| `Nalus (Berol. apud Nicolai).` | BOP |
| `neutre` | BUR |
| `Nominativ` | GRA |
| `Nāga.` | INM |
| `name; when alone = name of a man or of a woman.` | MD |
| `Name (also = title or epithet)` | MW |
| `NALOPĀKHYĀNA in BÖHTLINGK'S Chrestomathie (GILD. Bibl. 49). Die BOPP'sche Ausgabe (GILD. Bibl. 99) ist durch N. (BOPP) bezeichnet.` | PWG |
| `Neuter.` | SHS |

### `M.` — Ману / маскулин / медиум

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **11**; строк легенд дословно: 11. Встречается в статьях словарей: ae,bhs,bur,cae,gra,md,mw,pw,pwg.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Mālavikāgnimitra (Bombay).` | AP90 |
| `Māhārāṣṭrī.` | BHS |
| `Matsyôpâkhyâna, i.e. episodium de diluvio.` | BOP |
| `masculin` | BUR |
| `Middle.` | CAE |
| `Mātaríśva` | GRA |
| `Marut.` | INM |
| `Manusmṛiti (in twelve adyāyas, Māndlik’s edition, 1886).` | LRV |
| `MĀNAVADHARMAŚĀSTRA. (vol. 1)` | PW |
| `MANU'S Gesetzbuch in der Ausg. von LOISELEUR DESLONGCHAMPS (GILD. Bibl. 289).` | PWG |
| `Masculine.` | SHS |

### `S.` — Сутра / простое / см. (siehe)

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **5**; строк легенд дословно: 5. Встречается в статьях словарей: bhs,bur,cae,gra,lan,md,mw,pw,pwg.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `substantif` | BUR |
| `Simple.` | CAE |
| `Siehe` | GRA |
| `Sādhya.` | INM |
| `Sūtra.` | MD |

### `R.` — Рамаяна / корень / река

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **7**; строк легенд дословно: 7. Встречается в статьях словарей: bhs,mw,pw,pwg.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Raghuvaṃśa (Bombay).` | AP90 |
| `Rudra.` | INM |
| `Raghuvanśa (in nineteen sargas, Nirṇayasāgara edition, 1886).` | LRV |
| `river.` | MD |
| `RĀMĀYANA. Das 1ste und 2te Kāṇḍa nach der Ausg. von SCHLEGEL, das 3--6te nach der von GORRESIO, das 7te nach der Bomb. Ausg., wenn nicht ausdrücklich eine andere Ausgabe genannt ist. Eine eingeklammerte Zahl bezieht ist sich auf ed. Bomb. (vol. 1)` | PW |
| `RĀMĀYAṆA. Ohne eine nähere Angabe ist bei den zwei ersten Büchern die Ausgabe von SCHLEGEL (GILD. Bibl. 84), bei den vier letzten die von GORRESIO (GILD. Bibl. 85) gemeint.` | PWG |
| `Root.` | SHS |

### `K.` — Царь / Кадамбари / кинара

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **5**; строк легенд дословно: 5. Встречается в статьях словарей: bhs,gra,md,pw,pwg.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Kādambarī (Bombay).` | AP90 |
| `Kâs'inâthus, grammaticus indicus, cujus radicum collectionem edidit Wilkinsius (The radicals of the Sanscrita Language, London 1815). (****)` | BOP |
| `Karañja` | GRA |
| `Kinnara.` | INM |
| `king.` | MD |

### `H.` — Хитопадеша / небо / Хемачандра

Смыслов в цензе (нормализованный подсчёт ценза, `polysemy`): **5**; строк легенд дословно: 5. Встречается в статьях словарей: bhs,gra,pw,pwg,pwkvn.

| Строка легенды (дословно) | Словари легенды |
|---|---|
| `Hitopadeśa (Nirṇaya Sāgara Edition).` | AP90 |
| `Hidimbi caedes. (**)` | BOP |
| `Himmel` | GRA |
| `HEMAK4ANDRA'S ABHIDHĀNAK4INTĀMAṆI, Ausg. von BÖHTLINGK und RIEU. (vol. 1)` | PW |
| `HEMACANDRA'S ABHIDHĀNACINTĀMAṆI, ein systematisch angeordnetes synonymisches Lexicon. Herausgegeben, übersetzt und mit Anmer- kungen begleitet von OTTO BÖHTLINGK und CHARLES RIEU. St. Peters- burg 1847.` | PWG |

## Что не входит в ценз

Метка «нет в цензе» = у нас нет вычисленной строки; мы не пересказываем по памяти.

### `inj.` — Инъюнктив (вне ценза — см. реестр E3)

**Нет в цензе.** В `labelTable` ценза (H6409, снапшот 2026-10-10T19:00:00.879Z) строки `inj.` нет: расшифровка не вычислена, и мы её не толкуем. Для `inj.` это подтверждено независимо: реестр малых классов E3 (csl-standards v1.5.0, §2) держит форму декларативно-неразрешённой — attested-легенды в каноне нет.

## Если помету прочитал неверно — скажите об этом (обратная связь)

Гид — это тест на удобство регистра: **какие пометы студенты читают неверно — это сигнал**, который возвращается в реестр малых классов E3 (csl-standards v1.5.0). Одна строка обратной связи — одна ошибка чтения, схема поля: [data/schema/label-misread-feedback.schema.json](../data/schema/label-misread-feedback.schema.json). Правила: анонимный псевдоним пула (`pool-aNN`, никаких имён и контактов), дата в UTC без времени, поле `note` проходит ту же зачистку контактов, что и экспорт пула (§4.5 дизайн-документа пула), сырые строки живут в gitignored `review/` и в репозиторий не попадают; в репозиторий попадает только агрегат. Маршрут: строка → `review/` → агрегат → примечание в реестр E3 ([SMALL_CLASS_ABBREV_REGISTER_NOTE](https://github.com/gasyoun/csl-standards/blob/main/docs/SMALL_CLASS_ABBREV_REGISTER_NOTE.md)).

## Откуда взяты все числа (происхождение чисел)

| Число в гиде | Строка ценза |
|---|---|
| Всего сокращений в таблице: 34765 | `denominators.distinctLabelsInTable` |
| Строк с легендой: 4752 | `len(polysemy)` |
| Многозначных: 448 | `polysemy[*].nExpansions >= 2` (casefold-сравнение ценза) |
| Число смыслов у пометы (например, у `c.` — 4) | `polysemy["<label>"].nExpansions` |
| Расшифровки дословно | `labelTable["<label>"].legends[*].expansion` + `.dict` |
| Словари, где помета встречается в статьях | `labelTable["<label>"].tags` |

Снапшот ценза: 2026-10-10T19:00:00.879Z (H6409). Регенерация: `npm run build-abbrev-label-guide`; проверка байт-идентичности: `npm run build-abbrev-label-guide -- --check`.

