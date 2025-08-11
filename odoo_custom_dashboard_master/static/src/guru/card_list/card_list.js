/** @odoo-module **/

import { Component, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class GuruList extends Component {
  setup() {
    this.orm = useService("orm");
    this.action = useService("action");
    const today = new Date();
    this.state = {
      guruu: [],
      startDate: new Date(
        Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1, 0, 0, 1)
      )
        .toISOString()
        .split("T")[0],
      endDate: new Date(
        Date.UTC(
          today.getUTCFullYear(),
          today.getUTCMonth(),
          today.getUTCDate(),
          23,
          59,
          59,
          999
        )
      )
        .toISOString()
        .split("T")[0],
    };
    this.refreshInterval = null;
    this.countdownInterval = null;
    this.countdownTime = 10;
    this.isCountingDown = false;
    onWillStart(async () => {
      await this.fetchAllProducts();
    });

    onMounted(() => {
      this.attachEventListeners();
      this.filterDataByPeriod();
    });

    onWillUnmount(() => {
      // COUNTDOWN
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval);
      }
    });
  }

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
        if (this.state.startDate && this.state.endDate) {
          console.log(
            "dates state: ",
            this.state.startDate,
            "& ",
            this.state.endDate
          );
          const startDate = this.state.startDate;
          const endDate = this.state.endDate;
          console.log("dates: ", startDate, "& ", endDate);
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

  refreshChart(startDate, endDate) {
    this.fetchAllProducts();
  }

  async fetchAllProducts() {
    try {
      const filterDomain = [
        ["state", "=", "done"],
        ["siswa_id", "!=", false],
        ["jml_baris", ">", 0],
        // ["penanggung_jawab_id", "=", session.partner_display_name],
      ];

      if (this.state.startDate) {
        filterDomain.push(["tanggal", ">=", this.state.startDate]);
      }
      if (this.state.endDate) {
        filterDomain.push(["tanggal", "<=", this.state.endDate]);
      }

      const tahfidzRecords = await this.orm.searchRead(
        "cdn.tahfidz_quran",
        filterDomain,
        ["id", "siswa_id", "halaqoh_id", "jml_baris", "state", "tanggal"],
        { order: "jml_baris desc" }
      );

      console.log("Data Tahfidz", tahfidzRecords);

      this.state.guruu = this.getGuruData(tahfidzRecords);
      await this.render();
    } catch (error) {
      console.error("Error fetching Karyawan Data:", error);
    }
  }

  getGuruData(guruData) {
    const uniqueGuru = guruData.reduce((acc, data) => {
      const key = data.id;
      if (!acc[key]) {
        acc[key] = {
          name: Array.isArray(data.siswa_id) ? data.siswa_id[1] : data.siswa_id,
          halaqoh_id: Array.isArray(data.halaqoh_id)
            ? data.halaqoh_id[1]
            : data.halaqoh_id,
          jml_baris: data.jml_baris,
          // tanggal: data.tanggal,
          // status: data.state,
          id: data.id,
        };
      }
      return acc;
    }, {});

    return Object.values(uniqueGuru)
      .sort((a, b) => b.jml_baris - a.jml_baris)
      .slice(0, 10)
      .map((data, index) => ({
        number: index + 1,
        id: data.id,
        nama: data.name,
        halaqoh: data.halaqoh_id,
        baris: data.jml_baris || "N/A",
        // tgl: data.tanggal || "N/A",
        // status: data.status,
      }));
  }

  attachEventListeners() {
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const timerButton = document.getElementById("timerButton");

    if (timerButton) {
      timerButton.addEventListener("click", this.toggleCountdown.bind(this));
    } else {
      console.error("Timer button element not found");
    }

    if (startDateInput && endDateInput) {
      startDateInput.addEventListener("change", async (event) => {
        this.state.startDate = event.target.value;
        await this.fetchAllProducts();
      });

      endDateInput.addEventListener("change", async (event) => {
        this.state.endDate = event.target.value;
        await this.fetchAllProducts();
      });
    } else {
      console.error("Date input elements not found");
    }

    const today = new Date();
    let startDate = new Date(
      Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1, 0, 0, 1)
    );
    let endDate = new Date(
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
    // Add change listener to period selection dropdown
    if (periodSelection) {
      periodSelection.addEventListener("change", () => {
        switch (periodSelection.value) {
          case "7":
            startDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth(),
                today.getUTCDate() - 7
              )
            );
            endDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth(),
                today.getUTCDate()
              )
            );
            break;
          case "15":
            startDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth(),
                today.getUTCDate() - 15
              )
            );
            endDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth(),
                today.getUTCDate()
              )
            );
            break;
          case "month":
            // Set startDate to the 1st of the current month at 00:00:01 UTC
            startDate = new Date(
              Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1, 0, 0, 1)
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
          case "today":
            // Set startDate and endDate to today
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
            // Set startDate and endDate to yesterday
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
          case "lastMonth":
            startDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth() - 1,
                1,
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
          default:
            startDate = null;
            endDate = null;
        }

        // Update the input fields and the state
        if (startDate && endDate) {
          this.state.startDate = startDate.toISOString().split("T")[0];
          this.state.endDate = endDate.toISOString().split("T")[0];
          startDateInput.value = this.state.startDate;
          endDateInput.value = this.state.endDate;
          this.fetchAllProducts();
        }
      });
    }
  }

  updateDatesAndFilter(event) {
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");

    this.state.startDate = startDateInput.value || null;
    this.state.endDate = endDateInput.value || null;

    console.log("Updated Dates:", this.state.startDate, this.state.endDate);

    // Fetch and filter products based on updated date range
    this.fetchAllProducts();
  }

  filterData() {
    var startDate = document.getElementById("startDate")?.value;
    var endDate = document.getElementById("endDate")?.value;

    if (startDate && endDate) {
      this.fetchAllProducts(startDate, endDate);
      this.state.startDate = startDate;
      this.state.endDate = endDate;
    } else {
      this.fetchAllProducts();
    }
  }

  filterDataByPeriod() {
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const periodSelection = document.getElementById("periodSelection");

    // Langsung eksekusi logic tanpa mendaftarkan event listener baru
    const today = new Date();
    let startDate = new Date(
      Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1, 0, 0, 1)
    );
    let endDate = new Date(
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

    if (periodSelection) {
      periodSelection.addEventListener("change", () => {
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
          console.log("dates down: ", startDate, "& ", endDate);
          console.log(
            "dates down state: ",
            this.state.startDate,
            "& ",
            this.state.endDate
          );

          this.fetchAllProducts(startDate, endDate);
        }
      });
    }
  }

  redirectToGuruList(guruId) {
    try {
      console.log(guruId);
      return this.action.doAction({
        type: "ir.actions.act_window",
        name: "Top Santri Hafalan Terbanyak",
        res_model: "cdn.tahfidz_quran",
        res_id: guruId,
        views: [[false, "form"]],
        target: "current",
        domain: [["id", "=", guruId]],
      });
    } catch (error) {
      console.error("Error in redirectToProductList:", error);
    }
  }

  onGuruClick(guruId) {
    this.redirectToGuruList(guruId);
  }
}

export class EkskulList extends Component {
  setup() {
    this.orm = useService("orm");
    this.action = useService("action");
    const today = new Date();
    this.state = {
      guruu: [],
      startDate: new Date(
        Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1, 0, 0, 1)
      )
        .toISOString()
        .split("T")[0],
      endDate: new Date(
        Date.UTC(
          today.getUTCFullYear(),
          today.getUTCMonth(),
          today.getUTCDate(),
          23,
          59,
          59,
          999
        )
      )
        .toISOString()
        .split("T")[0],
    };
    this.refreshInterval = null;
    this.countdownInterval = null;
    this.countdownTime = 10;
    this.isCountingDown = false;
    onWillStart(async () => {
      await this.fetchAllProducts();
    });

    onMounted(() => {
      this.attachEventListeners();
      this.filterDataByPeriod();
    });

    onWillUnmount(() => {
      // COUNTDOWN
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval);
      }
    });
  }

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
        if (this.state.startDate && this.state.endDate) {
          console.log(
            "dates state: ",
            this.state.startDate,
            "& ",
            this.state.endDate
          );
          const startDate = this.state.startDate;
          const endDate = this.state.endDate;
          console.log("dates: ", startDate, "& ", endDate);
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

  refreshChart(startDate, endDate) {
    this.fetchAllProducts();
  }

  async fetchAllProducts() {
    try {
      const filterDomain = [];
      // filterDomain.push(["guru", "=", session.partner_display_name]);

      if (this.state.startDate) {
        filterDomain.push(["tanggal", ">=", this.state.startDate]);
      }
      if (this.state.endDate) {
        filterDomain.push(["tanggal", "<=", this.state.endDate]);
      }

      const kehadiranEkskul = await this.orm.searchRead(
        "cdn.absen_ekskul_line",
        filterDomain,
        ["id", "siswa_id", "guru", "ekskul", "kehadiran", "tanggal"]
      );

      console.log("Data Tahfidz", kehadiranEkskul);

      this.state.guruu = this.getGuruData(kehadiranEkskul);
      await this.render();
    } catch (error) {
      console.error("Error fetching Karyawan Data:", error);
    }
  }

  getGuruData(guruData) {
    const uniqueGuru = guruData.reduce((acc, data) => {
      const key = data.id;
      if (!acc[key]) {
        acc[key] = {
          name: Array.isArray(data.siswa_id) ? data.siswa_id[1] : data.siswa_id,
          nis: data.nis,
          kehadiran: data.kehadiran,
          tanggal: data.tanggal,
          pembimbing: Array.isArray(data.guru) ? data.guru[1] : data.guru,
          ekskul: Array.isArray(data.ekskul) ? data.ekskul[1] : data.ekskul,
          id: data.id,
        };
      }
      return acc;
    }, {});

    return Object.values(uniqueGuru).map((data, index) => ({
      number: index + 1,
      id: data.id,
      nama: data.name,
      nis: data.nis,
      kehadiran: data.kehadiran || "N/A",
      ekskul: data.ekskul || "N/A",
      pembimbing: data.pembimbing || "N/A",
    }));
  }

  attachEventListeners() {
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const timerButton = document.getElementById("timerButton");

    if (timerButton) {
      timerButton.addEventListener("click", this.toggleCountdown.bind(this));
    } else {
      console.error("Timer button element not found");
    }

    if (startDateInput && endDateInput) {
      startDateInput.addEventListener("change", async (event) => {
        this.state.startDate = event.target.value;
        await this.fetchAllProducts();
      });

      endDateInput.addEventListener("change", async (event) => {
        this.state.endDate = event.target.value;
        await this.fetchAllProducts();
      });
    } else {
      console.error("Date input elements not found");
    }

    const today = new Date();
    let startDate = new Date(
      Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1, 0, 0, 1)
    );
    let endDate = new Date(
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
    // Add change listener to period selection dropdown
    if (periodSelection) {
      periodSelection.addEventListener("change", () => {
        switch (periodSelection.value) {
          case "7":
            startDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth(),
                today.getUTCDate() - 7
              )
            );
            endDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth(),
                today.getUTCDate()
              )
            );
            break;
          case "15":
            startDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth(),
                today.getUTCDate() - 15
              )
            );
            endDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth(),
                today.getUTCDate()
              )
            );
            break;
          case "month":
            // Set startDate to the 1st of the current month at 00:00:01 UTC
            startDate = new Date(
              Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1, 0, 0, 1)
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
          case "today":
            // Set startDate and endDate to today
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
            // Set startDate and endDate to yesterday
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
          case "lastMonth":
            startDate = new Date(
              Date.UTC(
                today.getUTCFullYear(),
                today.getUTCMonth() - 1,
                1,
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
          default:
            startDate = null;
            endDate = null;
        }

        // Update the input fields and the state
        if (startDate && endDate) {
          this.state.startDate = startDate.toISOString().split("T")[0];
          this.state.endDate = endDate.toISOString().split("T")[0];
          startDateInput.value = this.state.startDate;
          endDateInput.value = this.state.endDate;
          this.fetchAllProducts();
        }
      });
    }
  }

  updateDatesAndFilter(event) {
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");

    this.state.startDate = startDateInput.value || null;
    this.state.endDate = endDateInput.value || null;

    console.log("Updated Dates:", this.state.startDate, this.state.endDate);

    // Fetch and filter products based on updated date range
    this.fetchAllProducts();
  }

  filterData() {
    var startDate = document.getElementById("startDate")?.value;
    var endDate = document.getElementById("endDate")?.value;

    if (startDate && endDate) {
      this.fetchAllProducts(startDate, endDate);
      this.state.startDate = startDate;
      this.state.endDate = endDate;
    } else {
      this.fetchAllProducts();
    }
  }

  filterDataByPeriod() {
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const periodSelection = document.getElementById("periodSelection");

    // Langsung eksekusi logic tanpa mendaftarkan event listener baru
    const today = new Date();
    let startDate = new Date(
      Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1, 0, 0, 1)
    );
    let endDate = new Date(
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

    if (periodSelection) {
      periodSelection.addEventListener("change", () => {
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
          console.log("dates down: ", startDate, "& ", endDate);
          console.log(
            "dates down state: ",
            this.state.startDate,
            "& ",
            this.state.endDate
          );

          this.fetchAllProducts(startDate, endDate);
        }
      });
    }
  }

  redirectToGuruList(guruId) {
    try {
      console.log(guruId);
      return this.action.doAction({
        type: "ir.actions.act_window",
        name: "Kehadiran Ekskul",
        res_model: "cdn.absen_ekskul_line",
        res_id: guruId,
        views: [[false, "form"]],
        target: "current",
        domain: [["id", "=", guruId]],
      });
    } catch (error) {
      console.error("Error in redirectToProductList:", error);
    }
  }

  onGuruClick(guruId) {
    this.redirectToGuruList(guruId);
  }
}

GuruList.template = "owl.GuruList";

EkskulList.template = "owl.EkskulList";
