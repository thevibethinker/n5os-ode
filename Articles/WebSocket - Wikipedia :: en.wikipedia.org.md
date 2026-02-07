---
url: https://en.wikipedia.org/wiki/WebSocket
---

# WebSocket - Wikipedia

WebSocket - Wikipedia

**WebSocket** is a computer [communications protocol](https://en.wikipedia.org/wiki/Communications_protocol "Communications protocol"), providing a [bidirectional](https://en.wikipedia.org/wiki/Full-duplex "Full-duplex") communication channel over a single [Transmission Control Protocol](https://en.wikipedia.org/wiki/Transmission_Control_Protocol "Transmission Control Protocol") (TCP) connection. The WebSocket protocol was standardized by the [IETF](https://en.wikipedia.org/wiki/Internet_Engineering_Task_Force "Internet Engineering Task Force") as [RFC](https://en.wikipedia.org/wiki/RFC_(identifier) "RFC (identifier)") [6455](https://www.rfc-editor.org/rfc/rfc6455) in 2011. The current specification allowing web applications to use this protocol is known as *WebSockets*.[5](https://en.wikipedia.org/wiki/WebSocket#fn:5) It is a living standard maintained by the [WHATWG](https://en.wikipedia.org/wiki/Web_Hypertext_Application_Technology_Working_Group "Web Hypertext Application Technology Working Group") and a successor to *The WebSocket API* from the [W3C](https://en.wikipedia.org/wiki/World_Wide_Web_Consortium "World Wide Web Consortium").[6](https://en.wikipedia.org/wiki/WebSocket#fn:6)

WebSocket is distinct from [HTTP](https://en.wikipedia.org/wiki/HTTP "HTTP") used to serve most webpages. Although they are different, [RFC](https://en.wikipedia.org/wiki/RFC_(identifier) "RFC (identifier)") [6455](https://www.rfc-editor.org/rfc/rfc6455) states that WebSocket "is designed to work over HTTP ports 443 and 80 as well as to support HTTP proxies and intermediaries", making the WebSocket protocol compatible with HTTP. To achieve compatibility, the WebSocket [handshake](https://en.wikipedia.org/wiki/Handshake_(computing) "Handshake (computing)") uses the [HTTP Upgrade header](https://en.wikipedia.org/wiki/HTTP/1.1_Upgrade_header "HTTP/1.1 Upgrade header") [7](https://en.wikipedia.org/wiki/WebSocket#fn:7) to change from the HTTP protocol to the WebSocket protocol.

The WebSocket protocol enables [full-duplex](https://en.wikipedia.org/wiki/Duplex_(telecommunications)#Full_duplex "Duplex (telecommunications)") interaction between a [web browser](https://en.wikipedia.org/wiki/Web_browser "Web browser") (or other [client](https://en.wikipedia.org/wiki/Client_(computing) "Client (computing)") application) and a [web server](https://en.wikipedia.org/wiki/Web_server "Web server") with lower overhead than half-duplex alternatives such as HTTP [polling](https://en.wikipedia.org/wiki/Polling_(computer_science) "Polling (computer science)"), facilitating real-time data transfer from and to the server. This is achieved by providing a standardized way for the server to send content to the client without being first requested by the client, and allowing messages to be exchanged while keeping the connection open. In this way, a two-way ongoing conversation can take place between the client and the server. The communications are usually done over TCP [port](https://en.wikipedia.org/wiki/Port_(computer_networking) "Port (computer networking)") number 443 (or 80 in the case of unsecured connections), which is beneficial for environments that block non-web Internet connections using a [firewall](https://en.wikipedia.org/wiki/Firewall_(computing) "Firewall (computing)"). Additionally, WebSocket enables streams of messages on top of TCP. TCP alone deals with streams of bytes with no inherent concept of a message. Similar two-way browser–server communications have been achieved in non-standardized ways using stopgap technologies such as [Comet](https://en.wikipedia.org/wiki/Comet_(programming) "Comet (programming)") or [Adobe Flash Player](https://en.wikipedia.org/wiki/Adobe_Flash_Player "Adobe Flash Player").[8](https://en.wikipedia.org/wiki/WebSocket#fn:8)

Most browsers support the protocol, including [Google Chrome](https://en.wikipedia.org/wiki/Google_Chrome "Google Chrome"), [Firefox](https://en.wikipedia.org/wiki/Firefox "Firefox"), [Microsoft Edge](https://en.wikipedia.org/wiki/Microsoft_Edge "Microsoft Edge"), [Internet Explorer](https://en.wikipedia.org/wiki/Internet_Explorer "Internet Explorer"), [Safari](https://en.wikipedia.org/wiki/Safari_(web_browser) "Safari (web browser)") and [Opera](https://en.wikipedia.org/wiki/Opera_web_browser "Opera web browser").[9](https://en.wikipedia.org/wiki/WebSocket#fn:9)

The WebSocket protocol specification defines `ws` (WebSocket) and `wss` (WebSocket Secure) as two new [uniform resource identifier](https://en.wikipedia.org/wiki/Uniform_resource_identifier "Uniform resource identifier") (URI) schemes [10](https://en.wikipedia.org/wiki/WebSocket#fn:10) that are used for unencrypted and encrypted connections respectively. Apart from the scheme name and [fragment](https://en.wikipedia.org/wiki/Fragment_identifier "Fragment identifier") (i.e. `#` is not supported), the rest of the URI components are defined to use [URI generic syntax](https://en.wikipedia.org/wiki/Path_segment "Path segment").[11](https://en.wikipedia.org/wiki/WebSocket#fn:11)

History
-------

WebSocket was first referenced as TCPConnection in the [HTML5](https://en.wikipedia.org/wiki/HTML5 "HTML5") specification, as a placeholder for a TCP-based socket API.[12](https://en.wikipedia.org/wiki/WebSocket#fn:12) In June 2008, a series of discussions were led by [Michael Carter](https://en.wikipedia.org/wiki/Michael_Carter_(entrepreneur) "Michael Carter (entrepreneur)") that resulted in the first version of the protocol known as WebSocket.[13](https://en.wikipedia.org/wiki/WebSocket#fn:13) Before WebSocket, port 80 full-duplex communication was attainable using [Comet](https://en.wikipedia.org/wiki/Comet_(programming) "Comet (programming)") channels; however, Comet implementation is nontrivial, and due to the TCP handshake and HTTP header overhead, it is inefficient for small messages. The WebSocket protocol aims to solve these problems without compromising the security assumptions of the web.
The name "WebSocket" was coined by [Ian Hickson](https://en.wikipedia.org/wiki/Ian_Hickson "Ian Hickson") and Michael Carter shortly thereafter through collaboration on the #whatwg IRC chat room,[14](https://en.wikipedia.org/wiki/WebSocket#fn:14) and subsequently authored for inclusion in the HTML5 specification by Ian Hickson. In December 2009, Google Chrome 4 was the first browser to ship full support for the standard, with WebSocket enabled by default.[15](https://en.wikipedia.org/wiki/WebSocket#fn:15) Development of the WebSocket protocol was subsequently moved from the W3C and [WHATWG](https://en.wikipedia.org/wiki/WHATWG "WHATWG") group to the IETF in February 2010, and authored for two revisions under Ian Hickson.[16](https://en.wikipedia.org/wiki/WebSocket#fn:16)

After the protocol was shipped and enabled by default in multiple browsers, the [RFC](https://en.wikipedia.org/wiki/RFC_(identifier) "RFC (identifier)") [6455](https://www.rfc-editor.org/rfc/rfc6455) was finalized under Ian Fette in December 2011.

[RFC](https://en.wikipedia.org/wiki/RFC_(identifier) "RFC (identifier)") [7692](https://www.rfc-editor.org/rfc/rfc7692) introduced compression extension to WebSocket using the [DEFLATE](https://en.wikipedia.org/wiki/DEFLATE "DEFLATE") algorithm on a per-message basis.

Web API
-------

A web application (e.g. web browser) may use the `WebSocket` interface to maintain bidirectional communications with a WebSocket server.[17](https://en.wikipedia.org/wiki/WebSocket#fn:17)

### Client example

In [TypeScript](https://en.wikipedia.org/wiki/TypeScript "TypeScript").

```
// Connect to server
const ws: WebSocket = new WebSocket("wss://game.example.com/scoreboard");

// Receive ArrayBuffer instead of Blob
ws.binaryType = "arraybuffer";

// Set event listeners

ws.onopen = (): void => {
    console.log("Connection opened");
    ws.send("Hi server, please send me the score of yesterday's game");
};

ws.onmessage = (event: MessageEvent): void => {
    console.log("Message received", event.data);
    ws.close(); // We got the score so we don't need the connection anymore
};

ws.onclose = (event: CloseEvent): void => {
    console.log("Connection closed", event.code, event.reason, event.wasClean);
};

ws.onerror = (event: Event): void => {
    console.log("Connection closed due to error");
};
```

### WebSocket interface

| Type | Name [18](https://en.wikipedia.org/wiki/WebSocket#fn:18) | Description |
| --- | --- | --- |
| [Constructor](https://en.wikipedia.org/wiki/Constructor_(object-oriented_programming) "Constructor (object-oriented programming)") | `ws = new WebSocket(url: string, protocols?: string | string[])` | **Start opening handshake**.[19](https://en.wikipedia.org/wiki/WebSocket#fn:19)  * `url`: The [URL](https://en.wikipedia.org/wiki/URL "URL") as a `string` (not class `URL`) containing:   + **[Scheme](https://en.wikipedia.org/wiki/URL#scheme "URL")**: must be `ws`, `wss`, `http` or `https`.   + **[Host](https://en.wikipedia.org/wiki/URL#host "URL")**.   + Optional [port](https://en.wikipedia.org/wiki/URL#port "URL"): If not specified, 80 is used for `ws` and `http`, and 443 for `wss` and `https`.   + Optional [path](https://en.wikipedia.org/wiki/URL#path "URL").   + Optional [query](https://en.wikipedia.org/wiki/URL#query "URL").   + **No** [fragment](https://en.wikipedia.org/wiki/URL#fragment "URL"). * Optional `protocols`: A `string` or `string[]` used as the value of the `Sec-WebSocket-Protocol` header in the opening handshake.   Exceptions:   * `SyntaxError`:   + `url` parsing [1](https://en.wikipedia.org/wiki/WebSocket#fn:1) failed.   + `url` has an invalid scheme.   + `url` has a fragment.   + `protocols` has duplicate strings. |
| [Method](https://en.wikipedia.org/wiki/Method_(computer_programming) "Method (computer programming)") | `ws.send(data: string | Blob | ArrayBuffer | ArrayBufferView)` | **Send data message**.[20](https://en.wikipedia.org/wiki/WebSocket#fn:20)  * `data`: must be `string`, `Blob`, `ArrayBuffer` or `ArrayBufferView`.   Return: `undefined`.  Exceptions:   * `InvalidStateError`: `ws.readyState` is `CONNECTING`.   Note:   * If the data cannot be sent (e.g. because it would need to be buffered but the buffer is full), the connection is closed and onerror is fired. |
| `ws.close(code?: number, reason?: string)` | **Start** **closing handshake**.[21](https://en.wikipedia.org/wiki/WebSocket#fn:21)  * Optional `code`: If specified, must be 1000 (*Normal closure*) or in the range 3000 to 4999 (application-defined). Defaults to 1000. * Optional `reason`: If specified, must be a string whose [UTF-8](https://en.wikipedia.org/wiki/UTF-8 "UTF-8") encoding is no longer than 123 bytes. Defaults to an empty string.   Return: `undefined`.  Exceptions:   * `InvalidAccessError`: `code` is not 1000 nor is in the range 3000 to 4999. * `SyntaxError`: UTF-8-encoded `reason` is longer than 123 bytes.   Note:   * If `ws.readyState` is `OPEN` or `OPENING`, `ws.readyState` is set to `CLOSING` and the closing handshake starts. * If `ws.readyState` is `CLOSING` or `CLOSED`, nothing happens (because the closing handshake has already started). |
| [Event](https://en.wikipedia.org/wiki/Event_(computing) "Event (computing)") | `ws.onopen = (event: Event): void => {}` `ws.addEventListener("open", (event: Event): void => {})` | **Opening handshake succeeded**. `event` type is `Event`. |
| `ws.onmessage = (event: MessageEvent): void => {}` `ws.addEventListener("message", (event: MessageEvent): void => {})` | **Data message received.**[22](https://en.wikipedia.org/wiki/WebSocket#fn:22) `event` type is `MessageEvent`. This event is only fired if `ws.readyState` is `OPEN`.  * `event.data` contains the data received, of type:   + `string` for text.   + `Blob` or `ArrayBuffer` for binary (see `ws.binaryType`). * `event.origin` is a string containing `ws.url` but only with the scheme, host and port (if any) URL components. |
| `ws.onclose = (event: CloseEvent): void => {}` `ws.addEventListener("close", (event: CloseEvent): void => {})` | The underlying **TCP connection closed**. `event` type is `CloseEvent` containing:[23](https://en.wikipedia.org/wiki/WebSocket#fn:23) [24](https://en.wikipedia.org/wiki/WebSocket#fn:24) [25](https://en.wikipedia.org/wiki/WebSocket#fn:25) [26](https://en.wikipedia.org/wiki/WebSocket#fn:26)  * `event.code`: [status code](https://en.wikipedia.org/wiki/WebSocket#Status_codes) (integer). * `event.reason`: reason for closing (string). * `event.wasClean`: `true` if the TCP connection was closed after the closing handshake was completed; `false` otherwise.   Note:   * If the received *Close* frame contains a **payload**, `event.code` and `event.reason` get their value from the payload.  * If the received *Close* frame contains **no payload**, `event.code` is 1005 (*No code received*) and `event.reason` is an empty string.  * If **no *Close* frame** was received, `event.code` is 1006 (*Connection closed abnormally*) and `event.reason` is an empty string. |
| `ws.onerror = (event: Event): void => {}` `ws.addEventListener("error", (event: Event): void => {})` | **Connection closed due to error**. `event` type is `Event`. |
| [Attribute](https://en.wikipedia.org/wiki/Attribute_(computing) "Attribute (computing)") | `ws.binaryType` (`string`) | **Type of `event.data` in `ws.onmessage`** when a binary data message is received. Initially set to `"blob"` (`Blob` object). May be changed to `"arraybuffer"` (`ArrayBuffer` object).[27](https://en.wikipedia.org/wiki/WebSocket#fn:27) |
| Read-only attribute | `ws.url` (`string`) | **URL given to the `WebSocket` constructor** with the following transformations:  * If scheme is `http` or `https`, change it to `ws` or `wss` respectively. |
| `ws.bufferedAmount` (`number`) | **Number of bytes** of application data (UTF-8 text and binary data) that have been **queued using `ws.send()` but not yet transmitted to the network**. It resets to zero once all queued data has been sent. If the connection closes, this value will only increase, with each call to `ws.send()`, and never reset to zero.[28](https://en.wikipedia.org/wiki/WebSocket#fn:28) |
| `ws.protocol` (`string`) | **Protocol accepted by the server**, or an empty string if the client did not specify `protocols` in the `WebSocket` constructor. |
| `ws.extensions` (`string`) | **Extensions accepted by the server**. |
| `ws.readyState` (`number`) | **Connection state**. It is one of the constants below. Initially set to `CONNECTING`.[29](https://en.wikipedia.org/wiki/WebSocket#fn:29) |
| [Constant](https://en.wikipedia.org/wiki/Constant_(computer_programming) "Constant (computer programming)") | `WebSocket.CONNECTING = 0` | **Opening handshake is currently in progress**. The initial state of the connection.[30](https://en.wikipedia.org/wiki/WebSocket#fn:30) [31](https://en.wikipedia.org/wiki/WebSocket#fn:31) |
| `WebSocket.OPEN = 1` | **Opening handshake succeeded**. The client and server may send messages to each other.[32](https://en.wikipedia.org/wiki/WebSocket#fn:32) [33](https://en.wikipedia.org/wiki/WebSocket#fn:33) |
| `WebSocket.CLOSING = 2` | **Closing handshake is currently in progress**. Either `ws.close()` was called or a *Close* message was received.[34](https://en.wikipedia.org/wiki/WebSocket#fn:34) [35](https://en.wikipedia.org/wiki/WebSocket#fn:35) |
| `WebSocket.CLOSED = 3` | The underlying **TCP connection is closed**.[36](https://en.wikipedia.org/wiki/WebSocket#fn:36) [23](https://en.wikipedia.org/wiki/WebSocket#fn:23) [24](https://en.wikipedia.org/wiki/WebSocket#fn:24) |

Protocol
--------

![](data:image/png;base64,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) 

A diagram describing a connection using WebSocket

Steps:

1. **[Opening handshake](https://en.wikipedia.org/wiki/WebSocket#Opening_handshake)**: [HTTP request](https://en.wikipedia.org/wiki/HTTP#HTTP/1.1_request_messages "HTTP") and [HTTP response](https://en.wikipedia.org/wiki/HTTP#HTTP/1.1_response_messages "HTTP").
2. **[Frame-based message](https://en.wikipedia.org/wiki/WebSocket#Frame-based_message)** exchange: data, ping and pong messages.
3. **[Closing handshake](https://en.wikipedia.org/wiki/WebSocket#Closing_handshake)**: close message (request then echoed in response).

### Opening handshake

The client sends an **HTTP request** (**[method](https://en.wikipedia.org/wiki/HTTP#Request_methods "HTTP")** **GET**, **[version](https://en.wikipedia.org/wiki/HTTP#Summary_of_HTTP_milestone_versions "HTTP") ≥ 1.1**) and the server returns an **HTTP response** with **[status code 101](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#101 "List of HTTP status codes")** (*Switching Protocols*) on success. HTTP and WebSocket clients can connect to a server using the same port because the opening handshake uses HTTP. Sending additional HTTP headers (that are not in the table below) is allowed. HTTP headers may be sent in any order. After the *Switching Protocols* HTTP response, the opening handshake is complete, the HTTP protocol stops being used, and communication switches to a binary frame-based protocol.[37](https://en.wikipedia.org/wiki/WebSocket#fn:37) [38](https://en.wikipedia.org/wiki/WebSocket#fn:38)

HTTP headers relevant to the opening handshake

|  | Header | Value | Mandatory |
| --- | --- | --- | --- |
| Request | [Origin](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields#origin-request-header "List of HTTP header fields") [39](https://en.wikipedia.org/wiki/WebSocket#fn:39) | Varies | Yes (for browser clients) |
| [Host](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields#host-request-header "List of HTTP header fields") [40](https://en.wikipedia.org/wiki/WebSocket#fn:40) | Varies | Yes |
| Sec-WebSocket-Version [41](https://en.wikipedia.org/wiki/WebSocket#fn:41) | *13* |
| Sec-WebSocket-Key [42](https://en.wikipedia.org/wiki/WebSocket#fn:42) | [base64](https://en.wikipedia.org/wiki/Base64 "Base64") -encode(16-byte random [nonce](https://en.wikipedia.org/wiki/Cryptographic_nonce "Cryptographic nonce")) |
| Response | Sec-WebSocket-Accept [43](https://en.wikipedia.org/wiki/WebSocket#fn:43) | base64-encode([SHA1](https://en.wikipedia.org/wiki/SHA1 "SHA1") (Sec-WebSocket-Key + [*258EAFA5-E914-47DA-95CA-C5AB0DC85B11*](https://en.wikipedia.org/wiki/Magic_number_(programming) "Magic number (programming)"))) [2](https://en.wikipedia.org/wiki/WebSocket#fn:2) |
| Both | [Connection](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields#connection-request-header "List of HTTP header fields") [44](https://en.wikipedia.org/wiki/WebSocket#fn:44) [45](https://en.wikipedia.org/wiki/WebSocket#fn:45) | *Upgrade* |
| [Upgrade](https://en.wikipedia.org/wiki/HTTP/1.1_Upgrade_header "HTTP/1.1 Upgrade header") [46](https://en.wikipedia.org/wiki/WebSocket#fn:46) [47](https://en.wikipedia.org/wiki/WebSocket#fn:47) | *websocket* |
| Sec-WebSocket-Protocol [48](https://en.wikipedia.org/wiki/WebSocket#fn:48) | The request may contain a [comma-separated list](https://en.wikipedia.org/wiki/Comma-separated_list "Comma-separated list") of strings (ordered by preference) indicating [application-level protocols](https://en.wikipedia.org/wiki/Application_layer "Application layer") (built on top of WebSocket data messages) the client wishes to use. If the client sends this header, the server response must be one of the values from the list. | No |
| Sec-WebSocket-Extensions [49](https://en.wikipedia.org/wiki/WebSocket#fn:49) [50](https://en.wikipedia.org/wiki/WebSocket#fn:50) [51](https://en.wikipedia.org/wiki/WebSocket#fn:51) [52](https://en.wikipedia.org/wiki/WebSocket#fn:52) | Used to negotiate protocol-level extensions. The client may request extensions to the WebSocket protocol by including a comma-separated list of extensions (ordered by preference). Each extension may have a parameter (e.g. foo=4). The server may accept some or all extensions requested by the client. This field may appear multiple times in the request (logically equivalent to a single occurrence containing all values) and must not appear more than once in the response. |

Example request:[38](https://en.wikipedia.org/wiki/WebSocket#fn:38)

```
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Origin: http://example.com
Sec-WebSocket-Protocol: chat, superchat
Sec-WebSocket-Version: 13
```

Example response:[38](https://en.wikipedia.org/wiki/WebSocket#fn:38)

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
Sec-WebSocket-Protocol: chat
```

The following [Python](https://en.wikipedia.org/wiki/Python_(programming_language) "Python (programming language)") code generates a random `Sec-WebSocket-Key`.

```
import base64
import os

print(base64.b64encode(os.urandom(16)))
```

The following Python code calculates `Sec-WebSocket-Accept` using `Sec-WebSocket-Key` from the example request above.

```
import base64
import hashlib

KEY: bytes = b"dGhlIHNhbXBsZSBub25jZQ=="
MAGIC: bytes = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
print(base64.b64encode(hashlib.sha1(KEY + MAGIC).digest()))
```

`Sec-WebSocket-Key` and `Sec-WebSocket-Accept` are intended to prevent a [caching](https://en.wikipedia.org/wiki/Cache_(computing) "Cache (computing)") [proxy](https://en.wikipedia.org/wiki/HTTP_proxy "HTTP proxy") from re-sending a previous WebSocket conversation,[53](https://en.wikipedia.org/wiki/WebSocket#fn:53) and does not provide any authentication, privacy, or integrity.

Though some servers accept a short `Sec-WebSocket-Key`, many modern servers will reject the request with error "invalid Sec-WebSocket-Key header".

### Frame-based message

After the opening handshake, the client and server can, at any time, send **data messages** (text or binary) and **control messages** (*Close*, *Ping*, *Pong*) to each other. A message is composed of **one frame if unfragmented** or **at least two frames if fragmented**.

**Fragmentation** splits a message into **two or more frames**. It enables sending messages with initial data available but complete length unknown. Without fragmentation, the whole message must be sent in one frame, so the complete length is needed before the first byte can be sent, which requires a buffer.[54](https://en.wikipedia.org/wiki/WebSocket#fn:54) It was proposed to extend this feature to enable multiplexing several streams simultaneously (e.g. to avoid monopolizing a socket for a single large [payload](https://en.wikipedia.org/wiki/Payload_(computing) "Payload (computing)")), but the protocol extension was never accepted.[55](https://en.wikipedia.org/wiki/WebSocket#fn:55)

* An **unfragmented message** consists of one frame with **`FIN = 1`** and **`opcode ≠ 0`**.
* A **fragmented message** consists of one frame with **`FIN = 0`** and **`opcode ≠ 0`**, followed by zero or more frames with **`FIN = 0`** and **`opcode = 0`**, and terminated by one frame with **`FIN = 1`** and **`opcode = 0`**.

### Frame structure

| [Offset](https://en.wikipedia.org/wiki/Offset_(computer_science) "Offset (computer science)")   (bits) | Field [56](https://en.wikipedia.org/wiki/WebSocket#fn:56) | | Size   (bits) | Description |
| --- | --- | --- | --- | --- |
| 0 | FIN [57](https://en.wikipedia.org/wiki/WebSocket#fn:57) | | 1 | * 1 = **final frame** of a message. * 0 = message is fragmented and this is **not the final frame**. |
| 1 | RSV1 | | 1 | **Reserved. Must be 0** unless defined by an extension. If a non-zero value is received and none of the negotiated extensions defines the meaning of such a non-zero value, the connection must be closed.[58](https://en.wikipedia.org/wiki/WebSocket#fn:58) |
| 2 | RSV2 | | 1 |
| 3 | RSV3 | | 1 |
| 4 | [Opcode](https://en.wikipedia.org/wiki/Operation_code "Operation code") | | 4 | See [opcodes](https://en.wikipedia.org/wiki/WebSocket#Opcodes) below. |
| 8 | [Masked](https://en.wikipedia.org/wiki/Data_masking "Data masking") [59](https://en.wikipedia.org/wiki/WebSocket#fn:59) | | 1 | * **1 = frame is masked** (i.e. masking key is present and the payload has been [XORed](https://en.wikipedia.org/wiki/XOR "XOR") with the masking key). * **0 = frame is not masked** (i.e. masking key is not present). See [client-to-server masking](https://en.wikipedia.org/wiki/WebSocket#Client-to-server_masking) below. |
| 9 | Payload length [60](https://en.wikipedia.org/wiki/WebSocket#fn:60) | | 7, 7+16 or 7+64 | **Length of the payload** (extension data + application data) in bytes. * **0–125** = This is the payload length. * **126** = The following 16 bits are the payload length. * **127** = The following 64 bits ([MSB](https://en.wikipedia.org/wiki/Most_Significant_Bit "Most Significant Bit") must be 0) are the payload length. [Endianness](https://en.wikipedia.org/wiki/Endianness "Endianness") is **big-endian**. [Signedness](https://en.wikipedia.org/wiki/Signedness "Signedness") is **unsigned**. The **minimum** number of bits must be used to encode the length. |
| Varies | Masking key [61](https://en.wikipedia.org/wiki/WebSocket#fn:61) | | 0 or 32 | **Random nonce**. Present if the masked field is 1. The client generates a masking key for every masked frame. |
| Payload | Extension data | Payload length (bytes) | **Must be empty** unless defined by an extension. |
| Application data | Depends on the opcode |

#### Opcodes

| Frame type [62](https://en.wikipedia.org/wiki/WebSocket#fn:62) | | Opcode [63](https://en.wikipedia.org/wiki/WebSocket#fn:63) | Related [Web API](https://en.wikipedia.org/wiki/WebSocket#Web_API) | Description | Purpose | Fragmentable | Max. payload length (bytes) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Continuation frame | | 0 |  | Non-first frame of a fragmented message. | Message fragmentation |  | 2 63 − 1 [3](https://en.wikipedia.org/wiki/WebSocket#fn:3) |
| Non-control frame | Text | 1 | `send()`, `onmessage` | UTF-8-encoded text. | Data message | Yes |
| Binary | 2 | Binary data. |
|  | 3–7 |  | **Reserved** for further non-control frames. May be defined by an extension.[64](https://en.wikipedia.org/wiki/WebSocket#fn:64) |  |
| Control frame [65](https://en.wikipedia.org/wiki/WebSocket#fn:65) | Close | 8 | `close()`, `onclose` | The WebSocket **closing handshake starts upon either sending or receiving a *Close* frame**.[66](https://en.wikipedia.org/wiki/WebSocket#fn:66) It may prevent data loss by complementing the [TCP closing handshake](https://en.wikipedia.org/wiki/Transmission_Control_Protocol#Connection_termination "Transmission Control Protocol").[67](https://en.wikipedia.org/wiki/WebSocket#fn:67) No frame can be sent after sending a *Close* frame. If a *Close* frame is received and no prior *Close* frame was sent, a *Close* frame must be sent in response (typically echoing the status code received). The payload is optional, but if present, it must start with a two-byte big-endian unsigned integer **status code**, optionally followed by a UTF-8-encoded reason message not longer than 123 bytes.[68](https://en.wikipedia.org/wiki/WebSocket#fn:68) | Protocol state | No | 125 |
| Ping | 9 |  | May be used for [latency](https://en.wikipedia.org/wiki/Latency_(engineering) "Latency (engineering)") measurement, [keepalive](https://en.wikipedia.org/wiki/Keepalive "Keepalive") and [heartbeat](https://en.wikipedia.org/wiki/Heartbeat_(computing) "Heartbeat (computing)"). Both sides can **send a ping** (with any payload). Whoever receives it must, as soon as is practical, **send back a pong with the same payload**. A pong should be ignored if no prior ping was sent.[69](https://en.wikipedia.org/wiki/WebSocket#fn:69) [70](https://en.wikipedia.org/wiki/WebSocket#fn:70) [71](https://en.wikipedia.org/wiki/WebSocket#fn:71) |
| Pong | 10 |  |
|  | 11–15 |  | **Reserved** for further control frames. May be defined by an extension.[64](https://en.wikipedia.org/wiki/WebSocket#fn:64) |

#### Client-to-server masking

A **client must mask** all frames sent to the server. A **server must not mask** any frames sent to the client.[72](https://en.wikipedia.org/wiki/WebSocket#fn:72) Frame masking applies **XOR between the payload and the masking key**. The following [pseudocode](https://en.wikipedia.org/wiki/Pseudocode "Pseudocode") describes the algorithm used to both mask and unmask a frame.[61](https://en.wikipedia.org/wiki/WebSocket#fn:61)

```
for i from 0 to payload_length − 1
   payload[i] := payload[i] xor masking_key[i mod 4]
```

### Status codes

| Range [73](https://en.wikipedia.org/wiki/WebSocket#fn:73) | Allowed in *Close* frame | Code [74](https://en.wikipedia.org/wiki/WebSocket#fn:74) | Description |
| --- | --- | --- | --- |
| 0–999 | No |  | Unused |
| 1000–2999 (Protocol) | Yes | 1000 | Normal closure. |
| 1001 | Going away (e.g. browser tab closed; server going down). |
| 1002 | Protocol error. |
| 1003 | Unsupported data (e.g. endpoint only understands text but received binary). |
| No | 1004 | Reserved for future usage |
| 1005 | No code received. |
| 1006 | Connection closed abnormally (i.e. closing handshake did not occur). |
| Yes | 1007 | Invalid payload data (e.g. non UTF-8 data in a text message). |
| 1008 | Policy violated. |
| 1009 | Message too big. |
| 1010 | Unsupported extension. The client should write the extensions it expected the server to support in the payload. |
| 1011 | Internal server error. |
| No | 1015 | TLS handshake failure. |
| 3000–3999 | Yes |  | Reserved for libraries, frameworks and applications. Registered directly with [IANA](https://en.wikipedia.org/wiki/Internet_Assigned_Numbers_Authority "Internet Assigned Numbers Authority"). |
| 4000–4999 |  | Private use. |

In Python.

Note: `recv()` returns up to the amount of bytes requested. For readability, the code ignores that, thus it may fail in non-ideal network conditions.

```
import base64
import hashlib
import struct
from typing import Optional
from socket import socket as Socket

def handle_websocket_connection(ws: Socket) -> None:
    # Accept connection
    conn, addr = ws.accept()

    # Receive and parse HTTP request
    key: Optional[bytes] = None
    for line in conn.recv(4096).split(b"\r\n"):
        if line.startswith(b"Sec-WebSocket-Key"):
            key = line.split()[-1]

    if key is None:
        raise ValueError("Sec-WebSocket-Key not found")

    # Send HTTP response
    sec_accept = base64.b64encode(hashlib.sha1(key + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
    conn.sendall(
        b"\r\n".join([
            b"HTTP/1.1 101 Switching Protocols",
            b"Connection: Upgrade",
            b"Upgrade: websocket",
            b"Sec-WebSocket-Accept: " + sec_accept,
            b"",
            b"",
        ])
    )

    # Decode and print frames
    while True:
        byte0, byte1 = conn.recv(2)
        fin: int = byte0 >> 7
        opcode: int = byte0 & 0b1111
        masked: int = byte1 >> 7
        assert masked, "The client must mask all frames"
        if opcode >= 8:
            assert fin, "Control frames are unfragmentable"

        # Payload size
        payload_size: int = byte1 & 0b111_1111
        if payload_size == 126:
            payload_size, = struct.unpack(">H", conn.recv(2))
            assert payload_size > 125, "The minimum number of bits must be used"
        elif payload_size == 127:
            payload_size, = struct.unpack(">Q", conn.recv(8))
            assert payload_size > 2**16-1, "The minimum number of bits must be used"
            assert payload_size <= 2**63-1, "The most significant bit must be zero"
        if opcode >= 8:
            assert payload_size <= 125, "Control frames must have up to 125 bytes"

        # Unmask
        masking_key: bytes = conn.recv(4)
        payload: bytearray = bytearray(conn.recv(payload_size))
        for i in range(payload_size):
            payload[i] = payload[i] ^ masking_key[i % 4]

        print("Received frame", FIN, opcode, payload)

if __name__ == "__main__":
    # Accept TCP connection on any interface at port 80
    ws: Socket = Socket()
    ws.bind(("", 80))
    ws.listen()
    
    handle_websocket_connection(ws)
```

Browser support
---------------

A secure version of the WebSocket protocol is implemented in Firefox 6,[75](https://en.wikipedia.org/wiki/WebSocket#fn:75) Safari 6, Google Chrome 14,[76](https://en.wikipedia.org/wiki/WebSocket#fn:76) [Opera](https://en.wikipedia.org/wiki/Opera_(web_browser) "Opera (web browser)") 12.10 and [Internet Explorer](https://en.wikipedia.org/wiki/Internet_Explorer "Internet Explorer") 10.[77](https://en.wikipedia.org/wiki/WebSocket#fn:77) A detailed protocol test suite report [78](https://en.wikipedia.org/wiki/WebSocket#fn:78) lists the conformance of those browsers to specific protocol aspects.

An older, less secure version of the protocol was implemented in Opera 11 and [Safari](https://en.wikipedia.org/wiki/Safari_(web_browser) "Safari (web browser)") 5, as well as the mobile version of Safari in [iOS 4.2](https://en.wikipedia.org/wiki/IOS_4.2 "IOS 4.2").[79](https://en.wikipedia.org/wiki/WebSocket#fn:79) The BlackBerry Browser in OS7 implements WebSockets.[80](https://en.wikipedia.org/wiki/WebSocket#fn:80) Because of vulnerabilities, it was disabled in Firefox 4 and 5,[81](https://en.wikipedia.org/wiki/WebSocket#fn:81) and Opera 11.[82](https://en.wikipedia.org/wiki/WebSocket#fn:82) Using browser developer tools, developers can inspect the WebSocket handshake as well as the WebSocket frames.[83](https://en.wikipedia.org/wiki/WebSocket#fn:83)

| Protocol version | Draft date | Internet Explorer | Firefox [84](https://en.wikipedia.org/wiki/WebSocket#fn:84)   (PC) | Firefox   (Android) | Chrome   (PC, Mobile) | Safari   (Mac, iOS) | Opera   (PC, Mobile) | Android Browser |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [hixie-75](https://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-75) | February 4, 2010 |  |  |  | 4 | 5.0.0 |  |  |
| [hixie-76](https://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76)   [hybi-00](https://tools.ietf.org/html/draft-ietf-hybi-thewebsocketprotocol-00) | May 6, 2010   May 23, 2010 |  | 4.0   (disabled) |  | 6 | 5.0.1 | 11.00   (disabled) |  |
| [hybi-07](https://tools.ietf.org/html/draft-ietf-hybi-thewebsocketprotocol-07), v7 | April 22, 2011 |  | 6 [85](https://en.wikipedia.org/wiki/WebSocket#fn:85) [4](https://en.wikipedia.org/wiki/WebSocket#fn:4) |  |  |  |  |  |
| [hybi-10](https://tools.ietf.org/html/draft-ietf-hybi-thewebsocketprotocol-10), v8 | July 11, 2011 |  | 7 [87](https://en.wikipedia.org/wiki/WebSocket#fn:87) [4](https://en.wikipedia.org/wiki/WebSocket#fn:4) | 7 | 14 [88](https://en.wikipedia.org/wiki/WebSocket#fn:88) |  |  |  |
| [RFC](https://en.wikipedia.org/wiki/RFC_(identifier) "RFC (identifier)") [6455](https://www.rfc-editor.org/rfc/rfc6455), v13 | December, 2011 | 10 [89](https://en.wikipedia.org/wiki/WebSocket#fn:89) | 11 | 11 | 16 [90](https://en.wikipedia.org/wiki/WebSocket#fn:90) | 6 | 12.10 [91](https://en.wikipedia.org/wiki/WebSocket#fn:91) | 4.4 |

Server implementations
----------------------

* [Nginx](https://en.wikipedia.org/wiki/Nginx "Nginx") has supported WebSockets since 2013, implemented in version 1.3.13 [92](https://en.wikipedia.org/wiki/WebSocket#fn:92) including acting as a [reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy "Reverse proxy") and [load balancer](https://en.wikipedia.org/wiki/Load_balancing_(computing) "Load balancing (computing)") of WebSocket applications.[93](https://en.wikipedia.org/wiki/WebSocket#fn:93)

* [Apache HTTP Server](https://en.wikipedia.org/wiki/Apache_HTTP_Server "Apache HTTP Server") has supported WebSockets since July, 2013, implemented in version 2.4.5 [94](https://en.wikipedia.org/wiki/WebSocket#fn:94) [95](https://en.wikipedia.org/wiki/WebSocket#fn:95)
* [Internet Information Services](https://en.wikipedia.org/wiki/Internet_Information_Services "Internet Information Services") added support for WebSockets in version 8 which was released with [Windows Server 2012](https://en.wikipedia.org/wiki/Windows_Server_2012 "Windows Server 2012").[96](https://en.wikipedia.org/wiki/WebSocket#fn:96)
* [lighttpd](https://en.wikipedia.org/wiki/Lighttpd "Lighttpd") has supported WebSockets since 2017, implemented in lighttpd 1.4.46.[97](https://en.wikipedia.org/wiki/WebSocket#fn:97) lighttpd mod\_proxy can act as a reverse proxy and load balancer of WebSocket applications. lighttpd mod\_wstunnel can act as a WebSocket endpoint to transmit arbitrary data, including in [JSON](https://en.wikipedia.org/wiki/JSON "JSON") format, to a backend application. lighttpd supports WebSockets over HTTP/2 since 2022, implemented in lighttpd 1.4.65.[98](https://en.wikipedia.org/wiki/WebSocket#fn:98)
* [Eclipse Mosquitto](https://mosquitto.org/) This is an [MQTT broker](https://en.wikipedia.org/wiki/MQTT#MQTT_broker "MQTT"), but it supports the MQTT over WebSocket. So, it can be considered a type of WebSocket implementation.

ASP.NET Core have support for WebSockets using the `app.UseWebSockets();` middleware.[99](https://en.wikipedia.org/wiki/WebSocket#fn:99)

Security considerations
-----------------------

Unlike regular cross-domain HTTP requests, WebSocket requests are not restricted by the [same-origin policy](https://en.wikipedia.org/wiki/Same-origin_policy "Same-origin policy"). Therefore, WebSocket servers must validate the "Origin" header against the expected origins during connection establishment, to avoid cross-site WebSocket hijacking attacks (similar to [cross-site request forgery](https://en.wikipedia.org/wiki/Cross-site_request_forgery "Cross-site request forgery")), which might be possible when the connection is authenticated with [cookies](https://en.wikipedia.org/wiki/HTTP_cookie "HTTP cookie") or HTTP authentication. It is better to use tokens or similar protection mechanisms to authenticate the WebSocket connection when sensitive (private) data is being transferred over the WebSocket.[100](https://en.wikipedia.org/wiki/WebSocket#fn:100) A live example of vulnerability was seen in 2020 in the form of [Cable Haunt](https://en.wikipedia.org/wiki/Cable_Haunt "Cable Haunt").

Proxy traversal
---------------

WebSocket protocol client implementations try to detect whether the [user agent](https://en.wikipedia.org/wiki/User_agent "User agent") is configured to use a proxy when connecting to destination host and port, and if it is, uses [HTTP CONNECT](https://en.wikipedia.org/wiki/HTTP_tunnel#HTTP_CONNECT_method "HTTP tunnel") method to set up a persistent tunnel.

The WebSocket protocol is unaware of proxy servers and firewalls. Some proxy servers are transparent and work fine with WebSocket; others will prevent WebSocket from working correctly, causing the connection to fail. In some cases, additional proxy-server configuration may be required, and certain proxy servers may need to be upgraded to support WebSocket.

If unencrypted WebSocket traffic flows through an explicit or a transparent proxy server without WebSockets support, the connection will likely fail.[101](https://en.wikipedia.org/wiki/WebSocket#fn:101)

If an encrypted WebSocket connection is used, then the use of [Transport Layer Security](https://en.wikipedia.org/wiki/Transport_Layer_Security "Transport Layer Security") (TLS) in the WebSocket Secure connection ensures that an `HTTP CONNECT` command is issued when the browser is configured to use an explicit proxy server. This sets up a tunnel, which provides low-level end-to-end TCP communication through the HTTP proxy, between the WebSocket Secure client and the WebSocket server. In the case of transparent proxy servers, the browser is unaware of the proxy server, so no `HTTP CONNECT` is sent. However, since the wire traffic is encrypted, intermediate transparent proxy servers may simply allow the encrypted traffic through, so there is a much better chance that the WebSocket connection will succeed
... (truncated)