# Network Space Proxy Fingerprint Intelligence Collector (NSPFIC)

[![Security Status](https://img.shields.io/badge/Security-Strict_Compliance-green.svg)](https://github.com/rowanssv4)
[![Automated Workflow](https://github.com/rowanssv4/nspfic/actions/workflows/auto-update.yml/badge.svg)](https://github.com/rowanssv4/nspfic/actions)

[📄 English Description](#english-version) | [📄 中文版本](#中文版本)

---

## English Version

### 🚨 Crucial Statement: Strict Resource Constraint & Abuse Prevention
* **TOS Compliance**: This repository operates under strict compliance with the GitHub Terms of Service (TOS). 
* **Resource Optimization**: The automated data engineering pipeline executes seamlessly in **less than 25 seconds** per lifecycle run. It implements a core circuit-breaker mechanism to restrict third-party API penetration to **under 120 requests**, ensuring absolute zero strain on GitHub Actions compute infrastructure or external network carrier bandwidth.
* **Legal Disclaimer & Local Law Compliance**: This project is exclusively developed as an open-source technical artifact for academic research, communication protocol analysis, and automated DevOps architecture training. **Users must strictly comply with all applicable local laws and regulations in their respective jurisdictions. The developer assumes absolutely no direct, joint, or collateral liability for any network penetration activities, data misuse, legal violations, or potential systemic risks resulting from users interacting with the generated datasets (`nodes.txt` / `sub.txt`). Use entirely at your own risk.**

---

### 1. What It Does
NSPFIC is an automated intelligence telemetry pipeline designed to harvest scattered, non-structured public proxy fingerprints from open-source threat intelligence pools. It dynamically de-obfuscates transport layer profiles, strips away structural configuration anomalies, performs authoritative autonomous system number (ASN) reverse-lookups, and persists normalized routing metrics into structured plaintext/ciphertext records.

### 2. The Purpose (Why This Tool)
The modern public routing landscape is heavily fragmented, polluted with invalid routing dead-ends, and flooded with falsified asset tags. The core purpose of this intelligence collector is to translate chaotic open-source spatial metadata into highly organized, multi-attribute network telemetry vectors. These standardized records serve as highly predictable infrastructure components for distributed network fault-tolerance simulations and telemetry mapping.

### 3. Technical Decisions (Why We Do It This Way)
* **The No-Ping Policy (Zero Active Probing)**: Traditional active connection testing (such as mass ICMP PING or heavy TCP handshake benchmarks) within automated virtualized environments heavily degrades network I/O queues. Dead-node timeouts inevitably lead to task stalling and trigger provider-level anti-DDoS firewalls. Moving active verification to client-side edge sorters ensures the scraping pipeline maintains an ultra-high throughput without processing lockups.
* **Dual-Engine Hybrid Fingerprinting**: To strictly bypass third-party provider rate-limits (429 Too Many Requests), the architecture bifurcates its workload: the top 120 high-weight seed streams are passed through an online API penetration engine to extract absolute carrier metadata (`+Residential`, `+Datacenter`, or specific backbone carriers); the remaining bulk data seamlessly switches to an offline 4-character lexical regex mapping matrix. This balances precision and velocity perfectly.
* **AST Structural Sanitization**: Payload validation filters are applied at the Abstract Syntax Tree (AST) layer prior to serialization, explicitly isolating and neutralizing embedded malicious HTML redirections or configuration exploits to guarantee a pure telemetry repository.

### 4. Infrastructure Selection (Why GitHub)
* **High-Availability Global Multi-Routing Edge**: GitHub Actions provides a pristine, containerized execution runtime equipped with enterprise-grade tier-1 network transit edges. This ensures maximum throughput and deterministic latency when fetching global, multi-region open-source telemetry feeds.
* **Frictionless Version-Controlled Storage**: Leveraging Git's native tree states allows for elegant, decentralized persistence without deploying or paying for traditional transactional databases. State delta records and automated operational telemetry logs are smoothly committed via standard headless bot push workflows.

---

## 中文版本

### 🚨 核心聲明：使用者在地法律遵循與防濫用規範
* **法律免責與風險自擔（核心）**：本项目屬純粹的開源技術研究產物，僅供學術研究、網路協定分析及自動化運維（DevOps）技術練習使用。**使用者在使用本專案或衍生資料時，必須嚴格遵守所在國家或地區的在地法律法規。任何因不當操作、違規使用或非法網路穿透行為所引發的法律訴訟、行政制裁或系統性風險，均由使用者本人承擔全部責任，專案開發者對此概不負責，亦不承擔任何直接、間接或連帶之法律責任。**
* **服務合規**：本專案嚴格遵循 GitHub 服務條款（TOS）的合規性框架執行。
* **高頻熔斷**：資料治理自動化流程的單次執行期嚴格控制在 **25 秒以內**。系統內建高頻請求熔斷器，將線上資料庫的深度查詢硬性限制在 **120 次以內**，杜絕任何濫用 GitHub Actions 免費運算資源與外部網路頻寬的行為。

---

### 1. 它做什麼 (What It Does)
本專案（NSPFIC）是一個全自動化的網路空間情報清洗流程。它能夠高頻並行採集網際網路中公開且無序散落的代理空間指紋載荷，進行深度的傳輸層特徵解包與結構化清洗，同時交叉比對全球權威 BGP 自主系統（ASN）歸屬，最終將帶有高價值路由標籤的資料寫入結構化的明文與密文資料集。

### 2. 做的目的 (Why This Tool)
公網中的分布式代理資產通常具備高度碎片化、瞬時失效且配置備註嚴重偽造的特徵。開發此收集器的核心目的，是為了將這些混雜的開源威脅情報與網路測繪原始資料，透過技術手段提煉並轉化為具備明確國別指紋、線路特質（如家寬/機房）的標準化遙測指標，作為分布式容災與網路拓撲模擬實驗的可靠數據基礎。

### 3. 為什麼這麼做 (Why We Do It This Way)
* **全面剝離主動驗證（No-Ping 策略）**：傳統的 TCP 三次握手並行測速或 ICMP PING 驗證，在自動化 CI/CD 虛擬環境下執行，極易因海量死節點的逾時（Timeout）堆積而造成 I/O 隊列嚴重卡死，甚至會被電信商防禦系統誤判為異常掃描而遭遇 IP 封鎖。因此本專案採用「全量釋出、移交用戶端在地非同步測速」的架構，確保核心流程能在數秒內維持極高吞吞吐量。
* **雙引擎混合指紋清洗矩陣**：為徹底規避外部權威地理資料庫的並行請求頻率限制（429 Too Many Requests），系統採取分流設計：前 120 個核心種子路徑會啟動線上 API 穿透，反查真實的 `+住宅IP`、`+商業機房` 或主干網拓撲特質；而 120 之後的後備載荷則無縫切換至在地輕量級 4 字詞法正規表示式（Regex）矩陣進行秒級認領，既防止被封鎖 IP，又實現了高精確度的全量標記。
* **抽象語法樹（AST）安全前置粗篩**：在將原始載荷序列化儲存之前，系統會執行特定的指紋粗篩，強行攔截並剔除所有包含惡意 HTML 網頁原始碼導向或異常偽裝的設定，確保下發資料池的絕對純淨度。

### 4. 為什麼選擇 GitHub (Why GitHub)
* **全球化多路由高可用邊緣運算**：GitHub Actions 提供了乾淨、具備全球頂級 BGP 互聯的跨國網路傳輸邊緣，能最大化保證並行拉取分布在不同國家和地區的開源網路資源時的傳輸效率與網路穩定性。
* **天然的版本控制情報庫**：利用 Git 的版本拓撲演進特性，可以在無需配置獨立、高成本關聯式資料庫的前提下，透過 Headless 機器人的強制作動（Force Push），無縫實現全域資料的增量覆蓋與執行狀態日誌的持久化，極大降低了輕量級極客專案的維運成本。
