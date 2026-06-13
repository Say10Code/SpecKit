---
title: "RuimTools: JavaCard source samples"
source: "http://www.ruimtools.com/doc.php?doc=javacard"
author:
published:
created: 2026-05-31
description:
tags:
  - "clippings"
---

**REFRESH** command  
  

```
private void MyRefresh() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  ph.init(PRO_CMD_REFRESH, (byte)0x00, DEV_ID_ME);

  //Should we want to carry out an update with a list of files, we could include this list
  //ph.appendTLV((byte)0x12, fileList, (short)0x00, (short)fileList.length);

  ph.send();

}
```

```
Available command qualifiers:

 '00' = NAA Initialization and Full File Change Notification;
 '01' = File Change Notification;
 '02' = NAA Initialization and File Change Notification;
 '03' = NAA Initialization;
 '04' = UICC Reset;
 '05' = NAA Application Reset, only applicable for a 3G platform;
 '06' = NAA Session Reset, only applicable for a 3G platform;
 '07' to 'FF' = reserved values.

Warnings: 

The Refresh with File Change Notification is not supported by many terminals
```

**PROVIDE LOCAL INFORMATION** command  
  

```
private void MyLocalInfo() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  ph.init(PRO_CMD_PROVIDE_LOCAL_INFORMATION, (byte)0x00, DEV_ID_ME);

  ph.send();

}
```

```
Available command qualifiers:

 '00' = Location Information according to current NAA;
 '01' = IMEI of the terminal;
 '02' = Network Measurement results according to current NAA;
 '03' = Date, time and time zone;
 '04' = Language setting;
 '05' = Reserved for GSM;
 '06' = Access Technology;
 '07' = ESN of the terminal;
 '08' = IMEISV of the terminal;
 '09' = Search Mode;
 '0A' = Charge State of the Battery (if class "X" is supported);
 '0B' = MEID of the terminal;
 '0C' to 'FF' = Reserved.

Warnings:

Networks measurement results not supported by many terminals.
 Location information very often unreliable. We do not get always the same response.
```

**SELECT ITEM** command  
  

```
private void MySelectItem() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  ph.init(PRO_CMD_SELECT_ITEM, DEFAULT_QUALIFIER, DEV_ID_ME);

  ph.appendTLV(TAG_ALPHA_IDENTIFIER, STR_MENSA6, (short)0, (short)STR_MENSA6.length);

  ph.appendTLV(TAG_ITEM_CR, (byte)1, item1, (short)0, (short)item1.length);

  ph.appendTLV(TAG_ITEM_CR, (byte)2, item2, (short)0, (short)item2.length);

  ph.appendTLV(TAG_ITEM_CR, (byte)3, item3, (short)0, (short)item3.length);

  ph.send();

}
```

```
Available command qualifiers:

 bit 1: 0 = presentation type is not specified;
    1 = presentation type is specified in bit 2.
 bit 2: 0 = presentation as a choice of data values if bit 1 = '1';
    1 = presentation as a choice of navigation options if bit 1 is '1'.
 bit 3: 0 = no selection preference;
    1 = selection using soft key preferred.
 bits 4 to 7: = RFU.
 bit 8: 0 = no help information available;
    1 = help information available.
```

**SEND SHORT MESSAGE** command  
  

```
private void MySendSMS() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  /*packing not required: */
  ph.init((byte)PRO_CMD_SEND_SHORT_MESSAGE, (byte)0x00, DEV_ID_NETWORK);        

  /*packing required: */
  //ph.init((byte)PRO_CMD_SEND_SHORT_MESSAGE, (byte)0x01, DEV_ID_NETWORK);

  ph.appendTLV(TAG_ALPHA_IDENTIFIER, STR_MENSA4, (short)0x00,
      (short)STR_MENSA4.length);

  /* SMC Address */
  ph.appendTLV((byte)TAG_ADDRESS, TMP_BUFFER, (short)0x01, (short)TMP_BUFFER[0]);

  /* MTA */
  //ph.appendTLV((byte)TAG_SMS_TPDU, TMP_BUFFER, (short)(TMP_BUFFER[0]+1), 
      //(short)(offset-(TMP_BUFFER[0]+1)));

  ph.send(); 

}
```

```
Available command qualifiers:

 bit 1: 0 = packing not required;
    1 = SMS packing by the ME required.
 bits 2 to 8: = 0 RFU.

Warnings:

When sending messages is a recommended practice to ensure that the server can cope 
 with the volume of generated messages.
```

**DISPLAY TEXT** command  
  

```
private void MyDisplayText() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  ph.init(PRO_CMD_DISPLAY_TEXT, (byte)(DTQ_HIGH_PRIORITY|DTQ_WAIT_FOR_USER),
      DEV_ID_DISPLAY);

  ph.appendTLV((byte)(TAG_TEXT_STRING|TAG_SET_CR), DCS_8_BIT_DATA, cad,
      (short)0, (short)clength);

  ph.send();

}
```

```
Available command qualifiers:

 bit 1: 0 = normal priority;
    1 = high priority.
 bits 2 to 7: = RFU.
 bit 8: 0 = clear message after a delay;
    1 = wait for user to clear message.

Warnings:

The Display Text Command with the command qualifier "wait for user" could generate 
 problems of reentrance with other applets. We must not forget that while the
 text is displayed no other proactive commands can be issued.
 This is a common source of problems with other applets
```

**SET UP CALL** command  
  

```
private void MySetUpCall() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  ph.init(PRO_CMD_SET_UP_CALL, (byte)0x02, DEV_ID_NETWORK);

  ph.appendTLV((byte)0x06, buffer_numbers ,(short)12, (short)longitud_numero);

  ph.appendTLV(TAG_ALPHA_IDENTIFIER, STR_MENSA3, (short)0, (short)STR_MENSA3.length);

  ph.send();

}
```

```
Available command qualifiers:

 '00' = set up call, but only if not currently busy on another call;
 '01' = set up call, but only if not currently busy on another call, with redial;
 '02' = set up call, putting all other calls (if any) on hold;
 '03' = set up call, putting all other calls (if any) on hold, with redial;
 '04' = set up call, disconnecting all other calls (if any);
 '05' = set up call, disconnecting all other calls (if any), with redial;
 '06' to 'FF' = reserved values.
```

**GET INPUT** command  
  

```
private void MyGetInput() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  ph.initGetInput(GIQ_NUMERIC, DCS_8_BIT_DATA, cad, (short)0, (short)cad.length, min, max);

  ph.send();

}
```

```
Available command qualifiers:

 bit 1: 0 = digits (0 to 9, *, #, and +) only;
    1 = alphabet set.
 bit 2: 0 = SMS default alphabet;
    1 = UCS2 alphabet.
 bit 3: 0 = terminal may echo user input on the display;
    1 = user input shall not be revealed in any way (see note).
 bit 4: 0 = user input to be in unpacked format;
    1 = user input to be in SMS packed format.
 bits 5 to 7: = RFU.
 bit 8: 0 = no help information available;
    1 = help information available.
```

**SET UP MENU** command  
  

```
private void MySetUpMenu() throws ToolkitException {

  tr = ToolkitRegistry.getEntry();

  // Register toolkit menu item.

  items[0] = tr.initMenuEntry(STR_TEST, (short)0, (short)STR_TEST.length,
      (byte)0, false, (byte)0, (byte)0);

}
```

```
Available command qualifiers:

 bit 1: 0 = no selection preference;
    1 = selection using soft key preferred.
 bits 2 to 7: = RFU.
 bit 8: 0 = no help information available;
    1 = help information available.

Warnings:

The maximum length and the number of the strings are contained also in the 
 installations parameters, so the number and the length of the menu entries must fit 
 within the allowed limits specified in the installation parameters.
 Besides the maximum length of the menu entries is also dependent on the EF_MENU ITEMS 
 record size, as a result the maximum length entered in the installation parameters 
 cannot exceed the allocated size in the record of the EF_MENU ITEMS.
```

**PLAY TONE** command  
  

```
private void MyPlayTome() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  ph.init(PRO_CMD_PLAY_TONE, (byte)0x00, (byte)0x03);

  ph.appendTLV((byte)(0x0E), (byte)0x01);

  ph.send();

}
```

```
Available command qualifiers:

 bit 1: 0 = use of vibrate alert is up to the terminal;
        1 = vibrate alert, if available, with the tone.
 bits 2 to 8: = 0 RFU
```

**LAUNCH BROWSER** command  
  

```
// http://wap.mygsm.com/stk/en
private final static byte[] WAP_url = {
  (byte)'h', (byte)'t', (byte)'t', (byte)'p', (byte)':', (byte)'/', (byte)'/',
  (byte)'w', (byte)'a', (byte)'p', (byte)'.', (byte)'m', (byte)'y', (byte)'g',
  (byte)'s', (byte)'m', (byte)'.', (byte)'c', (byte)'o', (byte)'m', (byte)'/',
  (byte)'s', (byte)'t', (byte)'k', (byte)'/', (byte)'e', (byte)'n',
};

private void MyLaunchBrowser() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  ph.init((byte)0x15/*LAUNCH BROWSER = 0x15*/, (byte)0x00, DEV_ID_ME);

  ph.appendTLV( (byte)0x31/*URL tag = 0x31*/, WAP_url, (short)0, (short)WAP_url.length);

  ph.send();

}
```

**Send USSD Javacard sample** command  
  

```
private final static byte[] array_ussd = {
    (byte)0x0F, (byte)0xAA, (byte)0x18, (byte)0x0C, (byte)0x36, (byte)0x02
};
// 0F - Data encoding scheme
// AA180C3602  - packed *100# string

private void Send_USSD() throws ToolkitException {

  ProactiveHandler ph = ProactiveHandler.getTheHandler();

  ph.init(PRO_CMD_SEND_USSD, (byte)0x00, DEV_ID_NETWORK);

  ph.appendTLV(TAG_USSD_STRING, array_ussd, (short)0x00, (short)array_ussd.length);

  ph.send();
}
```

```
Please note that the result of Send_USSD command will go to applet but not a screen.
The result must be received by ProactiveResponseHandler and then shown by DisplayText
```

**DES calculation**  
  

```
private DESKey MyDesKey;
private Cipher crypt_des;

private void MyDes() throws ToolkitException {

  MyDesKey = (DESKey) KeyBuilder.buildKey(KeyBuilder.TYPE_DES, KeyBuilder.LENGTH_DES, false);
  try {
    crypt_des = Cipher.getInstance(Cipher.ALG_DES_ECB_NOPAD, false);
  } catch (CryptoException e) {
    ISOException.throwIt((short) ((short) 0x9000 + e.getReason()));
  }

  MyDesKey.setKey(KeyArray, (short)KeyOffset);
  crypt_des.init(MyDesKey, Cipher.MODE_DECRYPT);
  crypt_des.doFinal(MyBuffer, (short)0, (short)DesLength, bytBuffer, (short)0);

}
```