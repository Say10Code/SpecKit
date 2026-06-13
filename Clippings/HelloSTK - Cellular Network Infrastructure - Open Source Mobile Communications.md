---
title: "HelloSTK - Cellular Network Infrastructure - Open Source Mobile Communications"
source: "https://osmocom.org/projects/cellular-infrastructure/wiki/HelloSTK"
author:
  - "[[dexter]]"
  - "[[12/10/2024 02:00 PM]]"
  - "[[03/17/2026 08:51 AM]]"
published:
created: 2026-05-31
description: "Redmine"
tags:
  - "clippings"
---
Actions

[History](https://osmocom.org/projects/cellular-infrastructure/wiki/HelloSTK/history)

## HelloSTK

HelloSTK is a collection of JAVA-card application examples. The examples make use of the sim toolkit (STK) to interact with the user. The examples mainly target [SysmoUSIM-SJS1](https://osmocom.org/projects/cellular-infrastructure/wiki/SysmoUSIM-SJS1), [SysmoISIM-SJA2](https://osmocom.org/projects/cellular-infrastructure/wiki/SysmoISIM-SJA2) and [SysmoISIM-SJA5](https://osmocom.org/projects/cellular-infrastructure/wiki/SysmoISIM-SJA5) cards, but should run on any card where applets have access to the sim-toolkit (STK) API.

## What is it about

(U)SIM cards are Java capable and there is the Globalplatform that specifies standards API. SMS can be addressed directly to the SIM card, the SIM card will get events for network selection and others, it can modify call establishment attempts.

The following will show how to build the example applet and install it on your USIM/ISIM. If you create plugins please make them available as Free Software and point us to them. If you find interesting Globalplatform APIs or hacks please talk about it.

## What you will need

- sysmoUSIM-SJS1 (or later model) card
- KIC, KID, KIK private keys of the card, including the KVN (Key Version Number)
- PCSC, serial card reader or be able to send SMS to the SIM card
- JDK to create Java1.1 bytecode to create/customize SIM Toolkit applets.
- GlobalPlatformPro (gp.jar) [https://javacard.pro/globalplatform/](https://javacard.pro/globalplatform/)

## What you can read

- JavaCard? API specification (http://www.andresteder.com/static/api/simtoolkitapi/sim/toolkit/package-summary.html)
- 3GPP sim.toolkit API (http://www.etsi.org/deliver/etsi\_ts/101400\_101499/101476/07.00.00\_60/ts\_101476v070000p.pdf). Specially setEvent is a good keyword to look at!
- 3GPP TS 31.102 Characteristics of the Universal Subscriber Identity Module (USIM) application, describes the file system in 4.7 [https://www.etsi.org/deliver/etsi\_ts/131100\_131199/131102/15.08.00\_60/ts\_131102v150800p.pdf](https://www.etsi.org/deliver/etsi_ts/131100_131199/131102/15.08.00_60/ts_131102v150800p.pdf)

## Building an example applet

- Clone hello-stk.git:  
	```
	$ git clone https://gitea.osmocom.org/sim-card/hello-stk
	```
- See README.md for detailed build instructions  
	[https://gitea.osmocom.org/sim-card/hello-stk/src/branch/master/README.md](https://gitea.osmocom.org/sim-card/hello-stk/src/branch/master/README.md)

## Managing applets

The following description is based on the attached (tryme.sh) script. You can either use the script or just replace the variables directly.

To perform any operation you need the key material of your card. The variables $KIC, $KID and $KIK must be populate with the proper key material. In addition to that, the Variable $KVN should contain the Key Version Number of the keyset to use. When set to 0 or when the --key-ver parameter is left out entirely, the first available keyset will be used. It should also be pointed out that the usage of incorrect key material may lock the card after a few attempts.

Unfortunately working with JAVA-card applets is a moving target. In case the current release of Globalplatform refuses to work, you may try version v20.08.12 as this version is known to work: [https://github.com/martinpaljak/GlobalPlatformPro/releases/tag/v20.08.12](https://github.com/martinpaljak/GlobalPlatformPro/releases/tag/v20.08.12)

#### Installing an applet

The variable $CAP should point to the.cap file that shall be installed. Since the applets make use of the sim toolkit (STK) a set of additional install parameters ($PARAMS) in the form of a hex-string (BER-TLV) is required (see GPC\_SPE\_034, Table 11-49 and ETSI TS 102 226, section 8.2.1.3.2). To install the presented sample applications, the following install parameters can be used:

```
PARAMS=c900ef1cc8020100c7020100ca12010001001505000000000000000000000000
```

To understand the install parameters, we may have a closer look using unber.py, which is included in pySim:

```
$ ./contrib/unber.py --hex c900ef1cc8020100c7020100ca12010001001505000000000000000000000000
c9 l=0 
ef l=28
  c8 l=2 0100
  c7 l=2 0100
  ca l=18 010001001505000000000000000000000000
```
The tag 0xC7 sets the Volatile Memory Quota and the tag 0xC8 sets the Non-volatile Memory Quota. The tag 0xCA is a series of bytes that contain the SIM File access and Toolkit Application Specific Parameters (ETSI TS 102 226 see also 8.2.1.3.2.1). In this example the following toolkit parameters are set:
- 0100: Access domain = 0x00 ==> file system access allowed
- 01: Priority level
- 00: Maximum allowed timers
- 15: Maximum length for a menue entry
- 05: Maximum number of menue entries

Equipped with this knowledge we can install the cap file:

```
java -jar ./gp.jar \
--key-enc $KIC \
--key-mac $KID \
--key-dek $KIK \
--key-ver $KVN \
--install $CAP \
--params $PARAMS
```

The result should be:

```
CAP loaded
```

#### Listing installed applets

```
java -jar ./gp.jar \
--key-enc $KIC \
--key-mac $KID \
--key-dek $KIK \
--key-ver $KVN \
--list
```

The result may look like this:

```
ISD: A000000003000000 (SECURED)
     Privs:    SecurityDomain, CardLock, CardTerminate
APP: A0000000871002FFFFFFFF8907090000 (SELECTABLE)
APP: A0000000871004FFFFFFFF8907090000 (SELECTABLE)
APP: A000000087ABCDFFFFFFFF8907090000 (SELECTABLE)
APP: 53696D62614E2E52414D (SELECTABLE)
APP: A0000000090001FFFFFFFF8900000000 (SELECTABLE)
     Privs:    CardReset
APP: 53696D62614E2E52464D (SELECTABLE)
APP: D07002CA44900101 (SELECTABLE)
PKG: A0000000620001 (LOADED)
PKG: 4A6176656C696E2E6A637265 (LOADED)
PKG: A0000000620101 (LOADED)
PKG: A0000000620102 (LOADED)
PKG: A0000000620201 (LOADED)
PKG: A000000062020801 (LOADED)
PKG: A00000006202080101 (LOADED)
PKG: A0000000620002 (LOADED)
PKG: A0000000620003 (LOADED)
PKG: A000000062010101 (LOADED)
PKG: A00000015100 (LOADED)
PKG: A0000000090005FFFFFFFF8911000000 (LOADED)
PKG: A0000000090005FFFFFFFF8912000000 (LOADED)
PKG: A0000000090005FFFFFFFF8913000000 (LOADED)
PKG: A0000000090005FFFFFFFF8911010000 (LOADED)
PKG: A0000000871005FFFFFFFF8913100000 (LOADED)
PKG: A0000000871005FFFFFFFF8913200000 (LOADED)
PKG: A0000000090003FFFFFFFF8910710001 (LOADED)
PKG: A0000000090003FFFFFFFF8910710002 (LOADED)
PKG: A0000000090005FFFFFFFF8915000000 (LOADED)
PKG: D07002CA44 (LOADED)
     Applet:   D07002CA44900101
```

The last item is the example applet.

#### Removing an applet

The variable $CAP should point to the.cap file that shall be removed.

```
java -jar ./gp.jar \
--key-enc $KIC \
--key-mac $KID \
--key-dek $KIK \
--key-ver $KVN \
--uninstall $CAP
```

The expected result is:

```
D07002CA44 deleted.
```

## Sample.cap file

The development of JAVA-card applets has a lot of pitfalls to offer. It may not immediately clear why a.cap file refuses to load. It may be due to a problem with GlobalPlatformPro or an incompatible combination of JAVA-card SDK and JDK or something completely different. To narrow down problems you find a tested.cap file (HelloSTK\_09122024.cap) attached.

Updated by [dexter](https://osmocom.org/users/15) [3 months](https://osmocom.org/projects/cellular-infrastructure/activity?from=2026-03-16 "03/16/2026 11:53 AM") ago · [10 revisions](https://osmocom.org/projects/cellular-infrastructure/wiki/HelloSTK/history)