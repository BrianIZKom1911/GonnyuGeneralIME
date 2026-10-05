# GonnyuGeneralIME — A General Gon(Gan) Chinese Input Method

> A digital writing system rooted in the Gon(Gan)–Poyang region.

Currently supports: **Lancong (Nanchang), Fenni (Fenyi), Fungcen (Fengcheng), Tiqien (Lichuan), Sinyi (Xinyu City), Songau (Shanggao), Seusong (Susong), Jingon (Ji'an), and Yikyan-Henfeng (Yiyang and Hengfeng)**. More localities are welcome.

**An easy-to-install Gon(Gan) input method for everyday use. Users familiar with Pinyin can get started with compatible support for Gon(Gan) romanisation and Mandarin Pinyin. Even users who do not speak Gon(Gan) can explore it, and Gon(Gan) expressions can also be used to write extended passages in Mandarin, including text like this document.**

**Native installation is available on macOS, Android, Windows, and Linux, alongside Rime resource packages.**

[![Rime Lancong (Nanchang)](https://img.shields.io/badge/Rime-Lancong%20%28Nanchang%29-0969da?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Doohaey/GonnyuGeneralIME-Rime-Lancong)
[![Rime Fenni (Fenyi)](https://img.shields.io/badge/Rime-Fenni%20%28Fenyi%29-8250df?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Doohaey/GonnyuGeneralIME-Rime-Fenni)
[![Rime Fungcen](https://img.shields.io/badge/Rime-Fungcen-e16a3d?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Doohaey/GonnyuGeneralIME-Rime-Fungcen)

Rime schema repositories for Lancong (Nanchang), Fenni (Fenyi), and Fungcen. Other installation options are available in the [Installation](#installation) section below.

## Release 1.1.0

- feat: Initialise the Tiqien, Songau, Seusong, Jingon, and Yikyan-Henfeng dialect dictionaries, and expand the Sinyi dictionary.
- feat: Add an entry to the Lancong dictionary and support typing locality names across dialect dictionaries.
- fix: Correct Fungcen readings and align regional dictionary spellings with their IPA transcriptions.
- fix: Correct regional transcription, tone, and checked-tone handling, and update the related romanisation guidance.
- feat: Merge reviewed Yikyan-Henfeng and Sinyi entries and complete the corresponding character readings.

## Contents

- [GonnyuGeneralIME — A General Gon(Gan) Chinese Input Method](#gonnyugeneralime--a-general-gongan-chinese-input-method)
  - [Release 1.1.0](#release-110)
  - [Contents](#contents)
  - [Overview](#overview)
    - [What it provides](#what-it-provides)
  - [See Gan in action](#see-gan-in-action)
    - [No learning needed, type by instinct](#no-learning-needed-type-by-instinct)
    - [Broad vocabulary, local life in full, rare characters no longer a barrier](#broad-vocabulary-local-life-in-full-rare-characters-no-longer-a-barrier)
    - [Gan and Mandarin, side by side](#gan-and-mandarin-side-by-side)
    - [Mandarin Pinyin, straight to Gan](#mandarin-pinyin-straight-to-gan)
    - [Literary or colloquial — clear at a glance](#literary-or-colloquial--clear-at-a-glance)
    - [Every Gan reading welcome, old and new](#every-gan-reading-welcome-old-and-new)
  - [Installation](#installation)
    - [macOS](#macos)
    - [iOS](#ios)
    - [Android](#android)
    - [Windows](#windows)
    - [Linux Fcitx5](#linux-fcitx5)
    - [Rime](#rime)
  - [The Gon-pin Romanisation](#the-gon-pin-romanisation)
    - [Initials](#initials)
    - [Finals](#finals)
      - [Open finals](#open-finals)
      - [Front-vowel finals](#front-vowel-finals)
      - [Rounded finals](#rounded-finals)
      - [Rounded front-vowel finals](#rounded-front-vowel-finals)
      - [Syllabic laterals and nasals](#syllabic-laterals-and-nasals)
      - [Other segments](#other-segments)
    - [Tones](#tones)
      - [Lancong (Nanchang)](#lancong-nanchang)
      - [Fungcen (Fengcheng)](#fungcen-fengcheng)
      - [Tiqien (Lichuan)](#tiqien-lichuan)
      - [Sinyi (Xinyu City)](#sinyi-xinyu-city)
      - [Songau (Shanggao)](#songau-shanggao)
      - [Seusong (Susong)](#seusong-susong)
      - [Jingon (Jian City)](#jingon-jian-city)
      - [Yikyan-Henfeng (Yiyang-Hengfeng)](#yikyan-henfeng-yiyang-hengfeng)
  - [References](#references)
    - [Literature](#literature)
    - [Dependency declarations](#dependency-declarations)
    - [Licensing and rights reservation](#licensing-and-rights-reservation)
    - [Acknowledgements](#acknowledgements)
  - [Origins: the loss of Gon(Gan)](#origins-the-loss-of-gongan)
  - [Contributors and contact](#contributors-and-contact)

## Overview

In the second half of 2025, we began thinking about creating a general Gon(Gan) input method, after observing input methods for other Sinitic languages. We initially assembled a basic dictionary by drawing on several sources to organise the correspondences between Gon(Gan) pronunciation and Chinese characters. We soon felt that simple sound-to-character mappings were insufficient for our needs. We wanted a more systematic way to organise and preserve language materials from different Gon(Gan)-speaking localities. The resulting project supports typing characters by their Gon(Gan) pronunciation, writing Mandarin through Gon(Gan) expressions, and producing idiomatic Gon(Gan) text even for younger people who have heard the language but are not proficient in it, or enthusiasts interested in Gon(Gan).

“General” has three meanings: use across Gon(Gan) localities, use across Gon(Gan) and Mandarin, and technical support across platforms.

Our project favours etymologically supported and standard character forms while accommodating common vernacular spellings, helping users write local Chinese that combines standard usage with familiar forms.

### What it provides

Beyond the dictionaries themselves, the input method currently provides:

- Pronunciation annotations for characters and words. The spelling system and tone notation are described below. It stays close to Hanyu Pinyin where possible to reduce the learning curve.
- Tolerant input for spelling habits familiar to Mandarin-input users, while presenting results in the project’s own spelling.
- Cross-references between common Mandarin words and local Gon(Gan) vocabulary. When either side is found, the corresponding expression is also offered as a candidate.
- Compatible input and clear annotation for literary and colloquial readings, newer and older readings, and other alternate pronunciations.

The project currently maintains nine regional dictionaries: urban Lancong (Nanchang), Fenni (Fenyi County in Xinyu), Fungcen, Tiqien (Lichuan), Sinyi (Xinyu City), Songau (Shanggao), Seusong (Susong), Jingon (Jian City), and Yikyan-Henfeng (Yiyang-Hengfeng). We hope to expand substantially to other localities as well. Contributions to add and correct dictionary entries are welcome.

## See Gan in action

<sub>The examples below use Nanchang Gan.</sub>

### No learning needed, type by instinct

Know Mandarin Pinyin and start typing right away. Enter a familiar Pinyin spelling, and the input method finds the corresponding Gan reading without requiring a separate input scheme.

![No learning needed, type by instinct](resources/images/selection/yue.png)

### Broad vocabulary, local life in full, rare characters no longer a barrier

Over 20,000 Chinese characters, including extensive coverage of Unicode Extension B with theoretical readings derived from rhyme dictionaries; over 100,000 words; abundant idiomatic local expressions; and distinctive pronunciations for place names. The dictionary goes far beyond a bare list of character readings.

![Broad coverage of local expressions](resources/images/selection/yongxyuot.png)
![Distinctive pronunciation for the place name Youkou](resources/images/selection/xiukieu.png)

### Gan and Mandarin, side by side

Type in Gan and see related Mandarin words at the same time. Recognise, confirm, and choose the word you want in one glance.

![Gan and Mandarin candidates together](resources/images/selection/goxiet.png)

### Mandarin Pinyin, straight to Gan

Have the Mandarin word in mind first? Type its familiar Pinyin and find the Gan expression right away.

![Type Gan text with Mandarin Pinyin](resources/images/selection/yitiandaowan.png)

### Literary or colloquial — clear at a glance

Gan everyday speech and written expression can sound different. The input method lays both readings out clearly, so your writing always fits the moment.

![Literary and colloquial reading example: miangnit](resources/images/selection/miangnit.png)

![Literary and colloquial reading example: minceu](resources/images/selection/minceu.png)

### Every Gan reading welcome, old and new

Alternate Gan pronunciations, including older and newer patterns, are all ready for input and lookup. Type the Gan you know, your way.

![Compatibility with alternate, older, and newer pronunciations](resources/images/selection/xiuji.png)


## Installation

The native input method is available for Linux, Android, Windows, and macOS. Installation of the universal Rime resource packages is described in the Rime section.

Packages for each operating system or locality are available from [Releases](https://github.com/Doohaey/GonnyuGeneralIME/releases).

### macOS

Download `GonnyuGeneralIME-version-macos.pkg` from [Releases](https://github.com/Doohaey/GonnyuGeneralIME/releases), open it, and complete the installation.

If it does not appear automatically, open **System Settings → Keyboard → Text Input → Edit…**, click **+**, search for and add **Gonnyu**, then select it from the input menu. Upgrades preserve the user dictionary.

If the input method is absent from the list in System Settings or cannot be selected after being added, signing out and back in may resolve the issue.

### iOS

iOS users can download **赣语输入法** from the App Store, except in the France storefront.

### Android

Download `GonnyuGeneralIME-version-android.apk` and open it on Android to install. On first launch, follow the in-app setup to enable the Gon(Gan) Chinese input method, then select it from the system input-method picker.

### Windows

Download and run `GonnyuGeneralIME-version-windows-installer.exe`. After the installer finishes, open **Settings → Time & language → Language & region → Chinese (Simplified) → Keyboards** and add **Gannyu**.

### Linux Fcitx5

Download `GonnyuGeneralIME-version-fcitx5.tar.gz`, extract it, and run the installer included in the archive:

```sh
tar -xzf GonnyuGeneralIME-version-fcitx5.tar.gz
cd GonnyuGeneralIME-version-fcitx5
./install.sh
```

Restart Fcitx5 with `fcitx5 -r`, or sign out and back in. Then add **Gannyu Gan / 赣语** in `fcitx5-configtool`.

### Rime

Download `GonnyuGeneralIME-version-rime-region.zip` for the required locality. The archive works with Rime front ends on every platform.

For Windows Weasel, copy the archive contents into `%APPDATA%\Rime` and redeploy from the input-method menu. For Linux Fcitx5 Rime, copy the contents into `~/.local/share/fcitx5/rime/`, redeploy, then select the locality from the schema menu. For iOS and Android, import or deploy the ZIP in the installed Rime front end.

## The Gon-pin Romanisation

The spelling system is intended to represent Gon(Gan) pronunciation while remaining as close as practical to the conventions of Hanyu Pinyin. To make typing easier and to accommodate mergers in newer varieties, some spellings deliberately accept more than one phoneme in a strict phonological sense.

### Initials

| gon-pin | Default IPA | Fungcen IPA | Tiqien IPA | Sinyi IPA | Songau IPA | Seusong IPA | Jingon IPA | Yikyan-Henfeng IPA | Accepted alternative input | Notes |
| --- | --- | --- | ------- | ------- | ------- | ------- | ------- | ------- | --- | --- |
| b | [p] | - | - | - | - | - | - | - |  |  |
| p | [pʰ] | - | - | - | - | - | - | - |  |  |
| m | [m] | - | - | - | - | - | - | - | - |  |
| f | [f] | - | - | - | - | - | - | - | — | May differ from Mandarin *f*; some descriptions use [ɸ]. |
| d | [t] | - | - | - | - | - | - | - |  |  |
| t | [tʰ] | - | - | - | - | - | - | - |  |  |
| l | [l] | - | - | - | - | - | - | - | - |  |
| z | [ts] | - | - | - | - | - | - | - |  |  |
| c | [tsʰ] | - | - | - | - | - | - | - |  |  |
| s | [s] | - | - | [θ] | - | - | - | - |  |  |
| j | [tɕ] | - | - | - | - | - | - | [tʃ] |  |  |
| q | [tɕʰ] | - | - | - | - | - | - | [tʃʰ] |  |  |
| n | [ȵ] | - | [n] | [n] | - | [n] or [ɳ] | - | [n] | - |  |
| x | [ɕ] | - | - | － | － | - | - | [ʃ] |  |  |
| g | [k] | - | - | - | - | - | - | - |  |  |
| k | [kʰ] | - | - | - | - | - | - | - |  |  |
| ng | [ŋ] | - | - | - | - | - | - | - | - | Velar nasal; example: 五 ng3. |
| h | [h] | [x] | - | [x] | [x] | [x] | [x] | [x] | — | The default [h] is articulated farther back than Mandarin h. |
| v | - | [v] | [v] | - | [v] | - | - | - |  |  |
| ch | - | - | - | - | - | [tʂʰ] | - | - |  |  |
| r | - | - | - | - | - | [ʐ] | - | - |  |  |
| sh | - | - | - | - | - | [ʂ] | - | - |  |  |
| zh | - | - | - | - | - | [tʂ] | - | - |  |  |

### Finals

Syllable-final `-n` and `-ng` match in both directions in every region.

Checked-tone codas follow these spelling and input rules.

- The IPA coda [ʔ] is written as `-k` in Gon-pin.
- Checked-tone codas may be omitted during input while still matching the corresponding readings.
- Each locality independently specifies a combination of `-t`, `-p`, and `-k`, or no checked-tone codas. The codas enabled for a locality are accepted interchangeably within that locality.

#### Open finals

| gon-pin | Default IPA | Fungcen IPA | Tiqien IPA | Sinyi IPA | Songau IPA | Seusong IPA | Jingon IPA | Yikyan-Henfeng IPA | Accepted alternative input | Notes |
| --- | --- | --- | ------- | ------- | ------- | ------- | ------- | ------- | --- | --- |
| ae | - | [æ] | - | - | [æ] | [æ] | [æ] | - | — |  |
| a | [a] | - | - | - | - | - | - | - | — |  |
| o | [o] | - | [ɔ] | - | - | - | [ɔ] | - | — |  |
| eo | [ɵ] | - | - | - | - | - | - | - | o, e (any position, one-way) |  |
| oe | - | - | - | - | - | - | [œ] or [ø] | - |  |  |
| e* | [e] | [ɛ] | [ɛ] | [ə] or [ɛ] | [ə] | - | [ə] or [ɛ] | [ə] or [ɛ] or [ɯ] | — |  |
| yng | - | - | - | - | - | - | - | [yŋ] |  |  |
| ai | [ai] | - | - | - | - | - | - | - | — |  |
| oi | [oi] | - | [ɔi] | [ɔi] | [ɔi] | - | [ɔi] | - | — |  |
| ei | [ei] or [ɨi] | [ɛi] | [ɛi] | [əi] | - | - | - | - | — | In Nanchang, [ei] occurs only in contracted pronunciations. |
| aeu | - | - | - | - | [æu] | - | - | - |  |  |
| au | [au] | [ɑu] | - | - | - | [ɑu] | - | - | ao |  |
| ou | - | - | [ɔu] | - | - | - | - | - | - |  |
| eu | [ɛu] or  [ɨu] | [əu] | - | [əu] or [ɪu] | - | [əu] | - | [əu] | ou (after some initials), ieu (after h) |  |
| am | - | [am] | [am] | - | - | - | - | - | — |  |
| om | - | - | [ɔm] | - | - | - | - | - | - |  |
| em | - | - | [ɛm] | - | - | - | - | - | - |  |
| aen | - | - | - | - | [æn] | - | - | - |  |  |
| an | [an] | - | - | - | - | - | - | - | — |  |
| on | [on] | - | [ɔn] | [ɔn] | [ɔn] | - | [ɔn] | - | — |  |
| en | [ɛn]  or  [ɨn] | [ən] | [ən] | [en] or [ɪn] | [ən] | [ən] | [ən] | [en] or [ɛen] | — |  |
| ang | [ɑŋ] | - | [aŋ] | [aŋ] | - | - | - | - | — |  |
| ong | [ɔŋ] | [oŋ] | - | [oŋ] | - | [oŋ] | - | - | on | Yikyan does not distinguish front and back variants of ong. |
| eng | - | [əŋ] | [ɛŋ] | - | - | - | [əŋ] | [əŋ] or [ən] | en | Most speakers no longer distinguish en and eng in Yikyan. |
| aet | - | [æt] | - | - | [æt] | - | - | - | — |  |
| at | [at] | - | - | - | - | - | - | - | — |  |
| ot | [ot] | - | - | - | [ɔt] | - | - | - | — |  |
| eot | - | [ɵt] | - | - | - | - | - | - | ot, et |  |
| et | [ɛt]  or  [ɨt] | - | - | - | - | - | - | - | — |  |
| aep | - | [æp] | - | - | - | - | - | - | — |  |
| ap | - | [ap] | [ap] | - | - | - | - | - | — |  |
| op | - | - | [ɔp] | - | - | - | - | - | — |  |
| eop | - | [ɵp] | - | - | - | - | - | - | op, ep |  |
| ep | - | - | [ɛp] | - | - | - | - | - | - |  |
| aek | - | [æʔ] or [æk] | - | - | [æʔ] | - | - | - | — |  |
| ak | [aʔ] | - | - | - | - | - | - | - | — |  |
| aik | - | - | [aiʔ] | [aiʔ] | - | - | - | - | - |  |
| ok | [ɔʔ] | [oʔ] | - | [oʔ] | - | - | - | - | — |  |
| eok | - | [ɵʔ] | - | - | - | - | - | - | ok, ek |  |
| oik | - | - | [ɔiʔ] | - | - | - | - | - | - |  |
| ek | - | [ɛʔ] or [ɨʔ] | [ɛʔ] | [əʔ] or [ɛʔ] | - | - | - | [ɛʔ] or [ɤʔ] or [ɪʔ] | — | [ɤʔ] can be written ek or uk. |
| euk | - | - | - | [ɪuʔ] | - | - | - | - | — |  |

\* Some regions use `ê` for IPA [ɛ] or [e]; input uses `e`. The same input spelling applies to `ê` in other finals and to ordinary `e`. Input `e` can match `ê` through one-way fuzzy matching.

#### Front-vowel finals

With no initial consonant:

- Before `-a`, `-o`, or `-e`, initial `i` is written `y`.
- In other positions, it is written `yi`.

| gon-pin | Default IPA | Fungcen IPA | Tiqien IPA | Sinyi IPA | Songau IPA | Seusong IPA | Jingon IPA | Yikyan-Henfeng IPA | Accepted alternative input | Notes |
| --- | --- | --- | ------- | ------- | ------- | ------- | ------- | ------- | --- | --- |
| i | [i]  or  [ɿ] | - | - | - | - | [ʅ] | - | - | — |  |
| ia | [ia] | - | - | - | - | - | - | - | — |  |
| iae | - | - | - | - | [iæ] | - | - | - |  |  |
| io | - | [iɔ] | [iɔ] | [io] | - | [io] | [io] or [iɔ] | - | - |  |
| ie | [iɛ] | - | - | [ie] | - | [ie] | - | - | — |  |
| iu* | [iu] | - | - | - | - | - | - | - | iu, you (no initial) |  |
| iai | - | - | - | [iai] | - | - | - | - | - |  |
| ioi | - | - | - | [ioi] or [iɔi] | - | - | - | - | - |  |
| iau | - | [iau] | [iau] | [iau] | - | [iɑu] | [iau] | [iau] | - |  |
| iaeu | - | - | - | - | [iæu] | - | - | - |  |  |
| iou | - | - | - | - | - | - | [iɔu] | - |  |  |
| ieu | [iɛu] | [iəu] | - | [iəu] | - | [iəu] | - | [iəu] | eu (after g, k, ng) |  |
| im | - | [im] | [im] | - | - | - | - | - | - |  |
| iam | - | - | [iam] | - | - | - | - | - | - |  |
| in | [in] | - | - | - | - | - | - | - | — |  |
| ian | - | [ian] | - | [ian] | [ian] | - | - | [ian] | - |  |
| iaen | - | - | - | - | [iæn] | - | - | - |  |  |
| ion | - | - | - | [ion] or [iɔn] | [iɔn] | - | - | - |  |  |
| ien | [iɛn] | - | - | [ien] | - | - | - | [ien] | - |  |
| iun | - | - | - | [iun] | - | - | - | - | - |  |
| ing | - | [iŋ] | [iŋ] | - | - | - | - | - | - |  |
| iang | [iɑŋ] | - | [iaŋ] | [iaŋ] | - | - | - | - | - |  |
| iong | [iɔŋ] | [ioŋ] | - | [ioŋ] | - | [ioŋ] | - | - | - |  |
| iung | [iuŋ] | - | - | - | - | - | - | - | - |  |
| it | [it] | - | - | - | - | - | - | - | — |  |
| iat | - | [iat] | - | - | - | - | - | - | - |  |
| iet | [iet] | [iɛt] | - | - | [iɛt] | - | - | - | - |  |
| ip | - | [ip] | [ip] | - | - | - | - | - | - |  |
| iap | - | [iap] | [iap] | - | - | - | - | - | - |  |
| iep | - | [iɛp] | - | - | - | - | - | - | — |  |
| ik | - | [iʔ] | [iʔ] | [ɿʔ] | - | - | - | [iʔ] |  |  |
| iak | [iaʔ] | - | - | [iɑʔ] | - | - | - | - | - |  |
| iaek | - | - | - | - | [iæʔ] | - | - | - |  |  |
| iaik | - | - | - | [iaiʔ] | - | - | - | - | - |  |
| iok | [iɔʔ] | - | - | [ioʔ] | - | - | - | - | - |  |
| iek | - | [iɛʔ] | [iɛʔ] | [iəʔ] or [iɛʔ] | [iɛʔ] | - | - | [iɛʔ] or [iɪʔ] |  |  |
| iuk | [iuʔ] | - | - | - | - | - | - | - | - |  |
| iuok | - | - | - | [iuɔʔ] | - | - | - | - | - |  |
| iuek | - | - | - | [iuəʔ] | - | - | - | - | - |  |

\* `iu`: Bare iu without an initial consonant is written yiu, distinct from yu for [y]; this distinction is omitted when a coda is present.

#### Rounded finals

With no initial consonant:

- Before `-a`, `-o`, `-e`, or `-i`, initial `u` is written `w`.
- In other positions, it is written `wu`.

| gon-pin | Default IPA | Fungcen IPA | Tiqien IPA | Sinyi IPA | Songau IPA | Seusong IPA | Jingon IPA | Yikyan-Henfeng IPA | Accepted alternative input | Notes |
| --- | --- | --- | ------- | ------- | ------- | ------- | ------- | ------- | --- | --- |
| u | [u] | - | - | - | - | [ʯ]* | - | - | - |  |
| un* | [un] or [uen] | [uɛn] | [uɛn] | - | - | [uən] or [ʯən] or [ʯɛn] | [uɛn] | [uɛn] | uen |  |
| ua | [ua] | - | - | - | - | - | - | - | - |  |
| uae | - | - | - | - | - | [uæ] or [ʯæ] | - | - |  |  |
| uo | [uo] | - | [uɔ] | - | - | - | - | - | - |  |
| ue | [ue] | [uɛ] | [uɛ] | - | - | - | [uɛ] | [uɛ] | - |  |
| ui* | [ui] or [uei] | [uɛi] | - | [uəi] | - | [ʯei] | - | - | uei, ui, wui (no initial), wei (no initial) |  |
| uie | - | [uiɛ] | - | - | - | - | - | - | wie (no initial) |  |
| uai | [uai] | - | - | - | - | [ʯai] | - | - | - |  |
| uoi | - | - | [uɔi] | [uoi] or [uɔi] | - | - | - | [uoi] | — |  |
| ueu | - | - | - | [uəu] | - | - | - | - | - |  |
| uan | [uan] | - | - | [uɑn] | - | - | - | - | - |  |
| uon | [uon] | - | [uɔn] | [uɔn] | - | - | [uɔn] | - | uen, wen (no initial) |  |
| uin | - | [uin] | - | - | - | - | - | - | - |  |
| uien | - | [uiɛn] | - | - | - | - | - | - | - |  |
| ung | [uŋ] | - | - | - | - | - | - | - | — |  |
| uang | [uɑŋ] | - | [uaŋ] | [uaŋ] | - | - | - | - | - |  |
| uong | [uɔŋ] | [uoŋ] | - | [uoŋ] | - | - | - | - | uon |  |
| ut | [ut] | - | - | - | - | - | - | - | - |  |
| uat | [uat] | - | - | - | - | - | - | - | - |  |
| uaet | - | [uæt] | - | - | - | - | - | - | - |  |
| uot | [uot] | - | - | - | - | - | - | - | - |  |
| uet | [uɛt] | [uɨt] | - | - | - | - | - | - | - |  |
| uep | - | [uɛp] | - | - | - | - | - | - | - |  |
| uk | [uʔ] | - | - | - | - | - | - | [ɤʔ] | - |  |
| uak | [uaʔ] | - | - | - | - | - | - | - | - |  |
| uaek | - | [uæʔ] | - | - | - | - | - | - | - |  |
| uaik | - | - | [uaiʔ] | - | - | - | - | - | - |  |
| uok | [uoʔ] | [uɔʔ] | [uɔʔ] | [uɔʔ] | - | - | - | [uɔʔ] | - |  |
| uoik | - | - | [uɔiʔ] | - | - | - | - | - | - |  |
| uek | — | [uɛʔ] or [uɨʔ] | [uɛʔ] | [uɛʔ] | - | - | - | [uəʔ] or [uɛʔ] or [uɤʔ] or [uɪʔ] | — |  |
| uik | - | [uɛiʔ] | [uiʔ] | [uəiʔ] | - | - | - | - | ueik, weik (no initial) |  |

\* `u`: The rounded postalveolar apical vowel [ʯ] is written u; finals beginning with [ʯ] also use u-series spellings. The vowel and its medial forms correspond to the front rounded series and are listed under rounded finals by spelling.

\* `uei`: `uei` and `uêi` are shortened to `ui` after an initial consonant and grouped under `ui` in this table. With no initial, the forms are `wei` and `wêi`; [ui] has the form `wi`.

\* `uen`: `uen` and `uên` are shortened to `un` after an initial consonant and grouped under `un` in this table. With no initial, the forms are `wen` and `wên`.


#### Rounded front-vowel finals

`yu` is provisionally used throughout for [y].

`yuo` inputs, including forms with initials or codas, match their original spelling only and do not expand through fuzzy matching.

| gon-pin | Default IPA | Fungcen IPA | Tiqien IPA | Sinyi IPA | Songau IPA | Seusong IPA | Jingon IPA | Yikyan-Henfeng IPA | Accepted alternative input | Notes |
| --- | --- | --- | ------- | ------- | ------- | ------- | ------- | ------- | --- | --- |
| yu | [y] | - | - | - | - | - | - | - | v (after an initial only), y, u |  |
| yueo | - | [yɵ] | - | - | - | - | - | - | yue |  |
| yue | [ye] | - | - | - | - | - | [yɛ] | [yɛ] | - |  |
| yng | - | - | - | - | - | - | - | [yŋ] |  |  |
| yun | [yn] | - | - | - | - | - | - | - | — |  |
| yuon | [yon] | - | - | - | - | - | [yɔn] | - | yoin (without an initial), yuen |  |
| yuen | - | - | - | - | - | - | [yɛn] | [yɛn] or [yɛŋ] | yueng |  |
| yung | - | [yŋ] | - | - | - | - | - | [yn] | yun |  |
| yuong | - | - | - | - | - | - | - | [yɔŋ] |  |  |
| yut | [yt] | - | - | - | - | - | - | - | - |  |
| yuot | [yot] | - | - | - | - | - | - | - | yue, yuet |  |
| yuet | - | [yet] | - | - | - | - | - | - | - |  |
| yuk | - | [yʔ] | [yʔ] | - | - | - | - | - | - |  |
| yuak | - | - | - | - | - | - | - | [yaʔ] | - |  |
| yuok | - | - | - | - | - | - | - | [yɔʔ] | - |  |
| yueok | - | [yɵʔ] | - | - | - | - | - | - | yuek |  |
| yuek | - | - | - | - | - | - | - | [yəʔ] or [yɛʔ] or [yɪʔ] | — |  |

#### Syllabic laterals and nasals

| gon-pin | Default IPA | Fungcen IPA | Tiqien IPA | Sinyi IPA | Songau IPA | Seusong IPA | Jingon IPA | Yikyan-Henfeng IPA | Notes |
| --- | --- | --- | --- | --- | --- | --- | ------- | ------- | --- |
| m | [m̩] | - | - | - | - | - | - | - |  |
| n | [n̩] | - | - | - | - | - | - | - |  |
| ng | [ŋ̩] | - | [ŋ̍] | [ŋ̍] | [ŋ̍] | - | [ŋ̍] | [ŋ̍] |  |
| l | - | - | - | - | - | [ɭ̩] | - | - |  |

#### Other segments

The system also records a number of extensions based on published descriptions and observed sound changes, including pronunciations recorded in a 1935 language survey and selected alternations involving `-n` and `-ng` codas.

### Tones

`0` denotes the neutral tone.

#### Lancong (Nanchang)

The Lancong (Nanchang) dictionary uses seven tone markers:

| Marker | Tone category | Pitch value |
| --- | --- | --- |
| 1 | yin level | 42 |
| 2 | yang level | 24 |
| 3 | rising | 213 |
| 4 | yin departing | 44(5) |
| 5 | yang departing | 21 |
| 6 | yin checked | 5 |
| 7 | yang checked | 1 or 2 |

#### Fungcen (Fengcheng)

The Fungcen (Fengcheng) dictionary uses six tone markers:

| Marker | Tone category | Pitch value |
| --- | --- | --- |
| 1 | yin level | 33 |
| 2 | yang level | 35 |
| 3 | rising | 213 |
| 4 | departing | 31 |
| 5 | yin checked | 1 |
| 6 | yang checked | 5 |

#### Tiqien (Lichuan)

The Tiqien (Lichuan) dictionary uses the following tone markers:

| Marker | Tone category | Pitch value |
| --- | --- | --- |
| 1 | yin level | 22 |
| 2 | yang level | 35 |
| 3 | rising | 44 |
| 4 | yin departing | 53 |
| 5 | yang departing | 13 |
| 6 | yin checked | 3 |
| 7 | yang checked | 5 |

#### Sinyi (Xinyu City)

The Sinyi (Xinyu City) dictionary uses the following tone markers:

| Marker | Tone category | Pitch value |
| --- | --- | --- |
| 1 | yin level A | 45 |
| 1* | yin level B | 24 |
| 2 | yang level | 33 |
| 3 | rising | 31 |
| 4 | departing | 11 |
| 5 | checked A | 5 |
| 5* | checked B | 24 |

#### Songau (Shanggao)

The Songau (Shanggao) dictionary uses the following tone markers:

| Marker | Tone category | Pitch value |
| --- | --- | --- |
| 1 | yin level | 31 |
| 2 | yang level | 24 |
| 3 | rising | 213 |
| 4 | departing | 51 |
| 5 | checked | 4 |

#### Seusong (Susong)

The Seusong (Susong) dictionary uses the following tone markers:

| Marker | Tone category | Pitch value |
| --- | --- | --- |
| 1 | yin level | 22 |
| 2 | yang level | 35 |
| 3 | rising | 51 |
| 4 | yin departing | 21 |
| 5 | yang departing | 314 |
| 6 | checked | 55 |

#### Jingon (Jian City)

The Jingon (Jian City) dictionary uses the following tone markers:

| Marker | Traditional tone category | Pitch value |
| --- | --- | --- |
| 1 | 阴平 | 334 |
| 2 | 阳平 | 11 |
| 3 | 上声 | 53 |
| 4 | 去声 | 214 |
| 5 | 高升调 | 35 |

#### Yikyan-Henfeng (Yiyang-Hengfeng)

The Yikyan-Henfeng (Yiyang-Hengfeng) dictionary uses the following tone markers:

| Marker | Traditional tone category | Pitch value |
| --- | --- | --- |
| 1 | 阴平 | 44 |
| 2 | 阳平 | 22 |
| 3 | 上声 | 412 |
| 4 | 阴去 | 45 |
| 5 | 阳去 | 212 |
| 6 | 阴入 | 5 |
| 7 | 阳入 | 4 |

## References

The project compiles its regional dictionaries from participants’ everyday language observations, academic publications, and dialect-enthusiast communities. Dictionary data and reference materials are made public as far as possible. Copyright enquiries can be sent to the contacts listed at the end of this document.

### Literature

1. osfans. **MCPDict** [CP/OL]. GitHub. <https://github.com/osfans/MCPDict>.
2. Xiong Zhenghui. *Literary and colloquial readings in the Lancong (Nanchang) dialect* [EB/OL]. <http://ling.cass.cn/keyan/xueshuchengguo/cgtj/202112/W020211223381176680381.pdf>. Accessed 2026-06-01.
3. Xiong Zhenghui. *Difficult characters in the Lancong (Nanchang) dialect* [EB/OL]. <http://ling.cass.cn/keyan/xueshuchengguo/cgtj/202112/W020211223381177519680.pdf>. Accessed 2026-06-04.
4. Xiong Zhenghui. *Dictionary of the Lancong (Nanchang) Dialect*.
5. Zhihu. “What vocabulary is distinctive enough to identify Gon(Gan) Chinese at once?” <https://www.zhihu.com/question/24262923/>.
6. Wikipedia. *Gon(Gan) Chinese original characters*. <https://gan.wikipedia.org/wiki/>.
7. Wikipedia. *Gon(Gan) Chinese*. <https://zh.wikipedia.org/zh-hans/%E8%B4%9B%E8%AA%9E>.
8. *Character-use standards for Chinese dialects, Language Resources Protection Project of China*. <http://www.moe.gov.cn/s78/A19/tongzhi/201704/W020170405307025943395.pdf>. Accessed 2026-08-04.
9. Bilibili. *New Concept Lancong (Nanchang) Dialect* series. <https://www.bilibili.com/video/BV1Us4y1C7fp/?share_source=copy_web&vd_source=5078721afbb2afc4394ca2602bb990de>.
10. Xiao Ping and Xiao Jiehan. *Dictionary of the Wucheng Dialect of Jiangxi* [M]. Beijing: The Commercial Press, 2017. Bibliographic information is listed in the [linguistic bibliography](https://geolinguistics.sakura.ne.jp/Monograph/SIG-Mono7-LAAA-3-ebook.pdf).

### Dependency declarations

The mobile input engine directly uses the following open-source projects. Exact revisions are pinned by the build lock; distributions retain the corresponding licences and copyright notices.

1. RIME Developers. **librime** `1.17.0`, BSD 3-Clause License. <https://github.com/rime/librime>
2. librime-lua Developers. **librime-lua** commit `ad1e4a6c98abf634dd34242a747f9b1d5d069fbe`, BSD 3-Clause License. <https://github.com/hchunhui/librime-lua>

### Licensing and rights reservation

The main project code is licensed under the GNU GPLv3; see `LICENSE` for details.
The name and branding “赣语通用输入法” (abbreviated as “赣语输入法”), together with the image at
`resources/icon.png`, are not covered by the GPLv3. All related copyrights, trademark rights,
and other rights are reserved by their respective rights holder. Use of the name or image in
derivative projects, redistributions, or commercial promotion requires permission.

Copyright in the project documentation belongs to the rights holder, with all rights reserved. Verbatim republication is permitted with attribution to the author and project.

### Acknowledgements

Special thanks to @豫章鸿也 for extensive advice on the project’s romanisation and character and word choices.

Given the scale of the dictionaries and the author's limited expertise and time, errors may remain. The author takes responsibility for them. Contributions of additions and corrections are appreciated.

## Origins: the loss of Gon(Gan)

> After three months of work, I wanted to add an essay introducing the project.

The Gon(Gan)–Poyang plain has long been an important economic and cultural hub in southern China, a densely populated land of rice and fish. Since the late Qing period, Jiangxi and neighbouring areas have experienced severe economic and demographic decline for various reasons. When the economic foundations of a flourishing culture collapse, its standing declines as well. Among southern Sinitic languages, Gon(Gan) now seems to have the weakest cultural presence. Gon(Gan)-speaking areas lack the clearly recognised standard pronunciation associated with Cantonese, the economic resources of Wu-speaking areas, the familiar cultural symbols and overseas influence of Southern Min, or the firm social foundations of Southwestern Mandarin and Sichuan speech in the densely settled Sichuan Basin. People who speak Gon(Gan) or grew up in Gon(Gan)-speaking areas often lack a clear understanding of their language. Their understanding tends to be a vague one shaped by administrative boundaries: Jiangxi speech, or one of the local varieties of Hunan, Hubei, Anhui, and so on. The familiar notion that pronunciation changes every ten li encourages a view of the region as a collection of disconnected local dialects.

Many local cities are now trying to develop cultural tourism, but culture needs distinctive features to sustain it. In common perceptions of its culture and social life, the Gon(Gan)–Poyang plain has become one of the least distinctive inland Han Chinese regions. The Jiangxi merchant networks and the saying “half the court's civil and military officials came from Jiangxi” are relics of the past. Jiangxi once had a flourishing scholarly tradition. The mindset of the imperial examinations remains deeply rooted, but there are too few strong universities and too little to attract talent from elsewhere. The former pursuit of culture now finds expression in fierce competition over the national college entrance examination. Successful students leave in large numbers instead of staying in hometowns they regard as ordinary and provincial.

At the same time, residents who see their region as lacking distinctive features have been particularly quick to abandon those they do have. Around the time I was born, Gon(Gan)-speaking areas were already abandoning their home language on a large scale, despite its history stretching back thousands of years, and treating it as rustic, backward, and nonstandard. In primary school, I showed my writing to classmates; when it came back, every instance of `好 X` had been changed, with good intentions, to `很 X`. Yet some people like me, who were taught Mandarin first, did not become proficient Mandarin speakers. Gon(Gan) left deep traces in our vowels and consonants, everyday speech, and vocabulary in school compositions. Our command could even be weaker than that of the previous generation's bilingual speakers, who had studied Mandarin systematically. In school essays, for example, I repeatedly used `紧` to mean “always”, actually corresponding to the `尽` in `尽管`, and frequently used `嘎` as a sentence-initial element. My Mandarin was, in effect, a “creole within the Sinitic family”. Some of my classmates from Nanchang, whose social lives were tightly controlled by parents focused on academic success, could no longer understand Nanchang Gon(Gan) at all, or even distinguish it from neighbouring languages. This degree of loss may be relatively rare among Sinitic-speaking communities.

Reports that most of the world's languages could disappear before the end of this century may leave most Sinitic-speaking communities unmoved. They may not realise that, if current trends continue, **their own languages**, the local Chinese spoken at home or in their hometowns, could also join the list of disappearing languages. Older patterns of social life and local social memory are being forgotten along with them. Later generations looking back at those communities may unconsciously assume that life in their streets and villages was conducted in Mandarin. Local ways of using language will be forgotten. For Sinitic-speaking communities, this would be a severe and profound cultural loss.

We believe our work is an important part of protecting Sinitic linguistic diversity.

## Contributors and contact

1. Dongche Xiye Editorial Department. Project planning and the Fenni (Fenyi) dictionary. <https://github.com/ComeRainOrComeShine>
2. Doohaey. Input-method framework and the Lancong (Nanchang) dictionary. Email: doohaey@gmail.com
3. Hialex. App icon design.
4. AstroChung. Yikyan (Yiyang) romanisation.
5. 江南西道客. Fungcen (Fengcheng) dictionary resources. Email: yunmoqingchen@qq.com.
6. 剑邑 Jason. Fungcen (Fengcheng) testing and feedback.
