<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/header-dark.svg" />
  <img src="./assets/header-light.svg" width="100%" alt="Eder Reyes Castellanos, backend developer in Villahermosa, Tabasco. A GPS track drives into the city over a map of its rivers and lagoons." />
</picture>
</p>

I build the backend side of GPS fleet tracking: services that pull telemetry from vendor platforms, store it in PostgreSQL + PostGIS, and turn it into routes, reports and regulatory feeds. Mostly Python (Django, FastAPI), and Rust where it has to be fast.

I also build LLM tooling, like a Text-to-SQL pipeline over a RAG system whose database roles only let the model read what it should. After hours I make pixel-art games in Phaser 4 and compose their music.

Open to freelance work and collaborations: [ederastonmartin@hotmail.com](mailto:ederastonmartin@hotmail.com)

## What I build

| Area | What it looks like in practice |
|---|---|
| 🛰️ **Vehicle tracking backends** | Services that ingest, validate and store GPS telemetry at scale, with geospatial queries (routes, geofences, positions) on PostgreSQL + PostGIS. |
| 📡 **Telemetry relay for compliance** | A GPS server that re-transmits vehicle positions to third-party / regulatory endpoints reliably and with traceability. |
| 🧾 **Business & regulatory automation** | Django modules that automate invoicing and volumetric-control records (receipts, deliveries, compliance reports). |
| 🤖 **LLM data access** | A Text-to-SQL pipeline over a RAG system (LangGraph + OpenAI/DeepSeek), with **hardened PostgreSQL roles** so the model can only read what it's allowed to. |
| ☁️ **Deployment & ops** | Dockerized services on Linux (CentOS) servers in Google Cloud Platform, with Redis for caching and queues. |

<sub>Details are kept generic on purpose. Happy to walk through architecture and trade-offs in a call.</sub>

## Platforms I've integrated

<table>
  <tr>
    <th>Area</th>
    <th width="240">Platforms</th>
    <th>What I did</th>
  </tr>
  <tr>
    <td>🛰️ <b>GPS telematics</b></td>
    <td>
      <a href="https://wialon.com"><img src="assets/platforms/wialon.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Wialon</a><br>
      <a href="https://www.mapon.com"><img src="assets/platforms/mapon.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Mapon</a><br>
      <a href="https://www.webfleet.com"><img src="assets/platforms/webfleet.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Webfleet</a><br>
      <a href="https://www.protrack365.com"><img src="assets/platforms/protrack.png" width="24" height="24" align="absmiddle" alt="">&nbsp;ProTrack</a>
    </td>
    <td>Synced units, positions, geofences and drivers into one console; reports and mileage.</td>
  </tr>
  <tr>
    <td>📹 <b>Video telematics</b></td>
    <td>
      <a href="https://www.streamax.com"><img src="assets/platforms/streamax.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Streamax</a><br>
      <a href="https://www.hikvision.com"><img src="assets/platforms/hikvision.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Hikvision</a><br>
      <a href="https://www.jimiiot.com"><img src="assets/platforms/jimiiot.png" width="24" height="24" align="absmiddle" alt="">&nbsp;JimiIoT</a>
    </td>
    <td>Live and recorded MDVR / camera video in the browser; alarm events relayed in real time by Node and Rust services.</td>
  </tr>
  <tr>
    <td>🗺️ <b>Maps &amp; geo</b></td>
    <td>
      <a href="https://mapsplatform.google.com"><img src="assets/platforms/google-maps.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Google&nbsp;Maps</a><br>
      <a href="https://www.openstreetmap.org"><img src="assets/platforms/openstreetmap.png" width="24" height="24" align="absmiddle" alt="">&nbsp;OpenStreetMap</a><br>
      <a href="https://leafletjs.com"><img src="assets/platforms/leaflet.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Leaflet</a>
    </td>
    <td>Geofences, route traces and geocoding (<a href="https://nominatim.org">Nominatim</a>) on top of PostGIS.</td>
  </tr>
  <tr>
    <td>🖨️ <b>Print fleet monitoring</b></td>
    <td>
      <a href="https://www.kpax-manage.com"><img src="assets/platforms/kpax.png" width="24" height="24" align="absmiddle" alt="">&nbsp;KPAX</a>
    </td>
    <td>Printer status, toner levels and consumption history in the console, through a Rust (actix&#8209;web) gateway with OAuth2 token caching.</td>
  </tr>
  <tr>
    <td>🧾 <b>ERP &amp; e&#8209;invoicing</b></td>
    <td>
      <a href="https://www.contpaqi.com"><img src="assets/platforms/contpaqi.png" width="24" height="24" align="absmiddle" alt="">&nbsp;CONTPAQi</a>
    </td>
    <td>Invoice stamping and cancellation through CONTPAQi.</td>
  </tr>
  <tr>
    <td>💬 <b>Messaging &amp; automation</b></td>
    <td>
      <a href="https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform"><img src="assets/platforms/whatsapp.png" width="24" height="24" align="absmiddle" alt="">&nbsp;WhatsApp&nbsp;Cloud&nbsp;API</a><br>
      <a href="https://n8n.io"><img src="assets/platforms/n8n.png" width="24" height="24" align="absmiddle" alt="">&nbsp;n8n</a><br>
      <a href="https://firebase.google.com/docs/cloud-messaging"><img src="assets/platforms/firebase.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Firebase&nbsp;Cloud&nbsp;Messaging</a>
    </td>
    <td>Invoices and payment receipts over WhatsApp, push notifications.</td>
  </tr>
  <tr>
    <td>🤖 <b>AI APIs</b></td>
    <td>
      <a href="https://openai.com/api/"><img src="assets/platforms/openai.png" width="24" height="24" align="absmiddle" alt="">&nbsp;OpenAI</a><br>
      <a href="https://api-docs.deepseek.com"><img src="assets/platforms/deepseek.png" width="24" height="24" align="absmiddle" alt="">&nbsp;DeepSeek</a><br>
      <a href="https://ai.google.dev/gemini-api"><img src="assets/platforms/gemini.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Gemini</a><br>
      <a href="https://www.voyageai.com"><img src="assets/platforms/voyage-ai.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Voyage&nbsp;AI</a>
    </td>
    <td>Text-to-SQL, document OCR from photos (vision models), embeddings for RAG.</td>
  </tr>
</table>

<!--
TODO: un-comment this section once the public demo repos exist (avoid 404 links).

---

## 🚀 Featured public projects

| Project | Stack | Description |
|---|---|---|
| [fastapi-postgis-tracker](https://github.com/Darkerc/fastapi-postgis-tracker) | FastAPI · PostGIS · Docker | Demo GPS tracking API with geofencing on synthetic data. |
| [rust-telemetry-relay](https://github.com/Darkerc/rust-telemetry-relay) | Rust · Tokio | Small, fast telemetry relay written in Rust. |
| [phaser-skins-demo](https://github.com/Darkerc/phaser-skins-demo) | Phaser 4 · JS | Character-skin system & state management demo with pixel art. |
| [Nuxt_MEVN_Scaffolding](https://github.com/Darkerc/Nuxt_MEVN_Scaffolding) | Nuxt · Express · MongoDB | Early full-stack MEVN scaffolding (archived learning project). |
-->

## Tech stack

<table>
  <tr>
    <td><b>Core</b></td>
    <td nowrap>
      <a href="https://www.python.org"><img src="assets/stack/python.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Python</a>&emsp;
      <a href="https://www.rust-lang.org"><img src="assets/stack/rust.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Rust</a>&emsp;
      <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img src="assets/stack/javascript.png" width="24" height="24" align="absmiddle" alt="">&nbsp;JavaScript</a><br>
      <a href="https://www.djangoproject.com"><img src="assets/stack/django.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Django</a>&emsp;
      <a href="https://fastapi.tiangolo.com"><img src="assets/stack/fastapi.png" width="24" height="24" align="absmiddle" alt="">&nbsp;FastAPI</a>&emsp;
      <a href="https://www.sqlalchemy.org"><img src="assets/stack/sqlalchemy.png" width="24" height="24" align="absmiddle" alt="">&nbsp;SQLAlchemy</a>&emsp;
      <a href="https://www.langchain.com/langgraph"><img src="assets/stack/langgraph.png" width="24" height="24" align="absmiddle" alt="">&nbsp;LangGraph</a><br>
      <a href="https://www.postgresql.org"><img src="assets/stack/postgresql.png" width="24" height="24" align="absmiddle" alt="">&nbsp;PostgreSQL</a>&emsp;
      <a href="https://postgis.net"><img src="assets/stack/postgis.png" width="24" height="24" align="absmiddle" alt="">&nbsp;PostGIS</a>&emsp;
      <a href="https://redis.io"><img src="assets/stack/redis.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Redis</a><br>
      <a href="https://www.docker.com"><img src="assets/stack/docker.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Docker</a>&emsp;
      <a href="https://www.kernel.org"><img src="assets/stack/linux.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Linux</a>&emsp;
      <a href="https://www.centos.org"><img src="assets/stack/centos.png" width="24" height="24" align="absmiddle" alt="">&nbsp;CentOS</a>&emsp;
      <a href="https://cloud.google.com"><img src="assets/stack/google-cloud.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Google&nbsp;Cloud</a>
    </td>
  </tr>
  <tr>
    <td><b>Also comfortable with</b></td>
    <td nowrap>
      <a href="https://vuejs.org"><img src="assets/stack/vue.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Vue</a>&emsp;
      <a href="https://nuxt.com"><img src="assets/stack/nuxt.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Nuxt</a>&emsp;
      <a href="https://nodejs.org"><img src="assets/stack/nodejs.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Node.js</a><br>
      <a href="https://www.php.net"><img src="assets/stack/php.png" width="24" height="24" align="absmiddle" alt="">&nbsp;PHP</a>&emsp;
      <a href="https://developer.mozilla.org/en-US/docs/Web/HTML"><img src="assets/stack/html.png" width="24" height="24" align="absmiddle" alt="">&nbsp;HTML</a>&emsp;
      <a href="https://developer.mozilla.org/en-US/docs/Web/CSS"><img src="assets/stack/css.png" width="24" height="24" align="absmiddle" alt="">&nbsp;CSS</a><br>
      <a href="https://git-scm.com"><img src="assets/stack/git.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Git</a>&emsp;
      <a href="https://github.com/features/actions"><img src="assets/stack/github-actions.png" width="24" height="24" align="absmiddle" alt="">&nbsp;GitHub&nbsp;Actions</a>&emsp;
      <a href="https://www.gnu.org/software/bash/"><img src="assets/stack/bash.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Bash</a>&emsp;
      <a href="https://www.postman.com"><img src="assets/stack/postman.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Postman</a>
    </td>
  </tr>
  <tr>
    <td><b>Exploring</b></td>
    <td nowrap>
      <a href="https://phaser.io"><img src="assets/stack/phaser.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Phaser&nbsp;4</a>&emsp;
      <a href="https://portswigger.net/burp"><img src="assets/stack/burp-suite.png" width="24" height="24" align="absmiddle" alt="">&nbsp;Burp&nbsp;Suite</a>
    </td>
  </tr>
</table>

## Activity

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./profile/streak-dark.svg" />
    <img src="./profile/streak.svg" alt="Contribution streak (includes private GitHub contributions and mirrored GitLab commits)" />
  </picture>
</p>

Most of my professional work lives in private repositories: on GitHub today, and on GitLab from 2020 to 2025. The GitLab commits are mirrored here as timestamps only (no code), so this chart is the best public trace of both.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./profile/history-dark.svg" />
  <img src="./profile/history.svg" alt="Contribution history since 2019, one cell per week, including private GitHub work and GitLab commits mirrored from 2020 to 2025" width="100%" />
</picture>

<!--
TODO: add the Top languages card back once public repos reflect the real stack
(today public repos are ~70% PHP from school projects).
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./profile/top-langs-dark.svg" />
  <img src="./profile/top-langs.svg" alt="Top languages" height="170" />
</picture>
-->

## Now

- **Learning:** Rust (async, systems tooling) and web security, working toward Burp Suite Certified Practitioner.
- **Building:** a pixel-art game in Phaser 4 (character skins, state management), with my own music and SFX.
- **Tinkering:** hardware security with a Flipper Zero.
