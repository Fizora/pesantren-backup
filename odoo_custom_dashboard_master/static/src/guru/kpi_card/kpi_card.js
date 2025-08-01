/** @odoo-module */

import { useService } from "@web/core/utils/hooks";
const { Component, useRef, onWillStart, onMounted, onWillUnmount, useState } =
  owl;
import { session } from "@web/session";

export class GuruKpiCard extends Component {
  setup() {
    this.orm = useService("orm");
    this.actionService = useService("action");
    this.refreshInterval = null;
    this.loadingOverlayRef = useRef("loadingOverlay");
    this.default_period = "thisMonth";
    this.state = useState({
      kpiData: [],
      startDate: null,
      endDate: null,
    });

    this.refreshInterval = null;
    this.countdownInterval = null;
    this.countdownTime = 10;
    this.isCountingDown = false;

    // Setup for component lifecycle events
    onWillStart(async () => {
      try {
        await this.updateKpiData();
      } catch (error) {
        console.error("Failed to update KPI data:", error);
      }
    });

    // Attach event listeners after mounting
    onMounted(() => {
      this.attachEventListeners();
      const periodSelection = document.getElementById("periodSelection");
      if (periodSelection) {
        periodSelection.value = "thisMonth"; // Pilih default "Bulan Ini"
      }
    });

    // Cleanup interval on component unmount
    onWillUnmount(() => {
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval);
      }
    });
  }

  // Loading Overlay
  showLoading() {
    if (!this.loadingOverlay) {
      this.loadingOverlay = document.createElement("div");
      this.loadingOverlay.innerHTML = ` <div class="musyrif-loading-overlay" style="
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.3);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 9999;
        ">
          <div class="loading-spinner">
            <i class="fas fa-sync-alt fa-spin fa-3x text-white"></i>
          </div>
        </div>`;
      document.body.appendChild(this.loadingOverlay);
    }
    if (this.loadingOverlay) {
      this.loadingOverlay.style.display = "flex";
    }
    this.state.isLoading = true;
  }
  hideLoading() {
    if (this.loadingOverlay) {
      this.loadingOverlay.style.display = "none";
    }

    this.state.isLoading = false;
  }

  // FUNC COUNTDOWN
  toggleCountdown() {
    if (this.isCountingDown) {
      // Jika sedang countdown, hentikan
      this.clearIntervals();
      document.getElementById("timerCountdown").textContent = "";
      const clockElement = document.getElementById("timerIcon");
      if (clockElement) {
        clockElement.classList.add("fas", "fa-clock");
      }
    } else {
      // Jika tidak sedang countdown, mulai baru
      this.isCountingDown = true; // Set flag sebelum memulai countdown
      this.startCountdown();
      const clockElement = document.getElementById("timerIcon");
      if (clockElement) {
        clockElement.classList.remove("fas", "fa-clock");
      }
    }
  }

  clearIntervals() {
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
      this.countdownInterval = null;
    }
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
    this.countdownTime = 10; // Reset countdown time
    this.isCountingDown = false; // Reset flag
  }

  startCountdown() {
    // Reset dan inisialisasi ulang
    this.countdownTime = 10;
    this.clearIntervals(); // Bersihkan interval yang mungkin masih berjalan
    this.updateCountdownDisplay();

    // Mulai interval baru
    this.countdownInterval = setInterval(() => {
      this.countdownTime--;

      if (this.countdownTime < 0) {
        this.countdownTime = 10;
        if (this.state.startDate2 && this.state.endDate2) {
          const startDate = this.state.startDate2;
          const endDate = this.state.endDate2;
          this.refreshChart(startDate, endDate);
        } else {
          this.refreshChart();
        }
      }

      this.updateCountdownDisplay();
    }, 1000);

    // Set flag bahwa countdown sedang berjalan
    this.isCountingDown = true;
  }

  updateCountdownDisplay() {
    const countdownElement = document.getElementById("timerCountdown");
    const timerIcon = document.getElementById("timerIcon");

    if (countdownElement) {
      countdownElement.textContent = this.countdownTime;
    }
  }

  refreshChart() {
    // Logika refresh chart
    console.log("Refreshing Card...");
    // Contoh penggunaan data fetching ulang
    this.updateKpiData();
  }

  async updateKpiData() {
    this.showLoading();
    try {
      const domain1 = [];
      const domain2 = [];
      const domain3 = [];
      const domain = [];
      if (this.state.startDate) {
        domain.push(["tanggal", ">=", this.state.startDate]);
        domain1.push(["tanggal", ">=", this.state.startDate]);
        domain2.push(["tanggal", ">=", this.state.startDate]);
        domain3.push(["tanggal", ">=", this.state.startDate]);
      }
      if (this.state.endDate) {
        domain.push(["tanggal", "<=", this.state.endDate]);
        domain1.push(["tanggal", "<=", this.state.endDate]);
        domain2.push(["tanggal", "<=", this.state.endDate]);
        domain3.push(["tanggal", "<=", this.state.endDate]);
      }

      domain.push(["penanggung_jawab_id", "=", session.partner_display_name]);
      domain1.push(["guru_id", "=", session.partner_display_name]);
      domain2.push(["guru_id", "=", session.partner_display_name]);

      let absensiTahfidz = await this.orm.call(
        "cdn.absen_tahfidz_quran",
        "search_read",
        [domain, ["name", "absen_ids"]]
      );

      let absensiSantri = await this.orm.call(
        "cdn.absensi_siswa",
        "search_read",
        [domain2, ["id", "kelas_id", "tanggal"]]
      );

      let absensiTahsin = await this.orm.call(
        "cdn.absen_tahsin_quran",
        "search_read",
        [domain, ["name", "absen_ids"]]
      );

      let absensiEkskul = await this.orm.call(
        "cdn.absensi_ekskul",
        "search_read",
        [domain3, ["id", "name"]]
      );

      let absenTahfidz = absensiTahfidz.length;
      let absenSantri = absensiSantri.length;
      let absenTahsin = absensiTahsin.length;
      let absenEkskul = absensiEkskul.length;

      this.state.kpiData = [
        {
          name: "Absen Siswa",
          value: absenSantri,
          icon: "fa-user-check",
          res_model: "cdn.absensi_siswa",
          domain: domain2,
        },
        {
          name: "Absen Tahfidz",
          value: absenTahfidz,
          icon: "fa-quran",
          res_model: "cdn.absen_tahfidz_quran",
          domain: domain,
        },
        {
          name: "Absen Tahsin",
          value: absenTahsin,
          icon: "fa-book",
          res_model: "cdn.absen_tahsin_quran",
          domain: domain,
        },
        {
          name: "Absen Ekskul",
          value: absenEkskul,
          icon: "fa-chalkboard-teacher",
          res_model: "cdn.absensi_ekskul",
          domain: domain3,
        },
      ];

      this.state.kpiData.forEach((kpi, index) => {
        const kpiElement = document.querySelector(`.kpi-value-${index}`);
        if (kpiElement) {
          animateValue(kpiElement, 0, kpi.value, 1000);
        }
      });
    } catch (error) {
      console.error("Error fetching KPI data:", error);
    } finally {
      this.hideLoading();
    }
  }

  attachEventListeners() {
    const kpiCards = document.querySelectorAll(".kpi-card");
    var timerButton = document.getElementById("timerButton");
    if (timerButton) {
      timerButton.addEventListener("click", this.toggleCountdown.bind(this));
    } else {
      console.error("Timer button element not found");
    }
    kpiCards.forEach((card) => {
      card.addEventListener("click", (evt) => {
        this.handleKpiCardClick(evt);
      });
    });

    // Add change listeners to date inputs
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const periodSelection = document.getElementById("periodSelection");

    if (startDateInput && endDateInput) {
      startDateInput.addEventListener("change", (event) => {
        this.state.startDate = event.target.value || null;
        this.updateKpiData();
      });
      endDateInput.addEventListener("change", (event) => {
        this.state.endDate = event.target.value || null;
        this.updateKpiData();
      });
    }
    const today = new Date();
    let startDate;
    let endDate;
    // Add change listener to period selection dropdown
    if (periodSelection) {
      this.showLoading();
      try {
        const handlePeriodChange = () => {
          switch (periodSelection.value) {
            case "today":
              // Hari Ini
              startDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  today.getUTCDate(),
                  0,
                  0,
                  0,
                  1
                )
              );
              endDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  today.getUTCDate(),
                  23,
                  59,
                  59,
                  999
                )
              );
              break;
            case "yesterday":
              // Kemarin
              startDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  today.getUTCDate() - 1,
                  0,
                  0,
                  0,
                  1
                )
              );
              endDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  today.getUTCDate() - 1,
                  23,
                  59,
                  59,
                  999
                )
              );
              break;
            case "thisWeek":
              // Minggu Ini
              const startOfWeek = today.getUTCDate() - today.getUTCDay(); // Set ke hari Minggu
              startDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  startOfWeek,
                  0,
                  0,
                  0,
                  1
                )
              );
              endDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  startOfWeek + 6,
                  23,
                  59,
                  59,
                  999
                )
              );
              break;
            case "lastWeek":
              // Minggu Lalu
              const lastWeekStart = today.getUTCDate() - today.getUTCDay() - 7; // Minggu sebelumnya
              startDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  lastWeekStart,
                  0,
                  0,
                  0,
                  1
                )
              );
              endDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  lastWeekStart + 6,
                  23,
                  59,
                  59,
                  999
                )
              );
              break;
            case "thisMonth":
              // Bulan Ini
              startDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  1,
                  0,
                  0,
                  0,
                  1
                )
              );
              endDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth() + 1,
                  0,
                  23,
                  59,
                  59,
                  999
                )
              );
              break;
            case "lastMonth":
              // Bulan Lalu
              startDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth() - 1,
                  1,
                  0,
                  0,
                  0,
                  1
                )
              );
              endDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  0,
                  23,
                  59,
                  59,
                  999
                )
              );
              break;
            case "thisYear":
              // Tahun Ini
              startDate = new Date(
                Date.UTC(today.getUTCFullYear(), 0, 1, 0, 0, 0, 1)
              );
              endDate = new Date(
                Date.UTC(today.getUTCFullYear(), 11, 31, 23, 59, 59, 999)
              );
              break;
            case "lastYear":
              // Tahun Lalu
              startDate = new Date(
                Date.UTC(today.getUTCFullYear() - 1, 0, 1, 0, 0, 0, 1)
              );
              endDate = new Date(
                Date.UTC(today.getUTCFullYear() - 1, 11, 31, 23, 59, 59, 999)
              );
              break;
            default:
              // Default ke Bulan Ini jika tidak ada yang cocok
              startDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth(),
                  1,
                  0,
                  0,
                  0,
                  1
                )
              );
              endDate = new Date(
                Date.UTC(
                  today.getUTCFullYear(),
                  today.getUTCMonth() + 1,
                  0,
                  23,
                  59,
                  59,
                  999
                )
              );
          }

          // Update the input fields and the state
          if (startDate && endDate) {
            this.state.startDate = startDate.toISOString().split("T")[0];
            this.state.endDate = endDate.toISOString().split("T")[0];
            startDateInput.value = this.state.startDate;
            endDateInput.value = this.state.endDate;

            this.updateKpiData();
          }
        };

        // Attach the listener for future changes
        periodSelection.addEventListener("change", handlePeriodChange);

        // Trigger the function immediately to apply the default filter on load
        handlePeriodChange();
      } catch {
        console.log("Terjadi Error");
      } finally {
        this.hideLoading();
      }
      // Set a default value for periodSelection (e.g., 'month')

      // Define the change event listener
    }
  }

  async handleKpiCardClick(evt) {
    this.clearIntervals();
    document.getElementById("timerIcon").className = "fas fa-clock";
    document.getElementById("timerCountdown").textContent = "";
    this.clearIntervals();
    this.updateCountdownDisplay();
    const cardName = evt.currentTarget.dataset.name;
    const cardData = this.state.kpiData.find((kpi) => kpi.name === cardName);
    if (cardData) {
      const { res_model, domain } = cardData;
      await this.actionService.doAction({
        name: `${cardName} Details`,
        type: "ir.actions.act_window",
        res_model: res_model,
        view_mode: "list",
        views: [[false, "list"]],
        target: "current",
        domain: domain,
      });
    } else {
      console.error(`No data found for KPI card: ${cardName}`);
    }
  }
}

GuruKpiCard.template = "owl.GuruKpiCard";
