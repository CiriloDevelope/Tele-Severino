// ============================================================
// JavaScript simples do protótipo
// ============================================================
// Futuro backend:
// - Aqui podem entrar chamadas fetch() para APIs reais.
// - Exemplo: fetch('/api/specialists'), fetch('/api/payment')
// - Para o protótipo, o Flask já entrega as páginas renderizadas.
// ============================================================


// Tela de carregamento laranja.
// Ela redireciona automaticamente para a rota definida em data-next.
const splash = document.querySelector(".splash-screen");
if (splash) {
  const nextUrl = splash.dataset.next || "/login";
  setTimeout(() => {
    window.location.href = nextUrl;
  }, 1200);
}


// Cronômetro da tela de chamada.
// Em produção, isso deve ser sincronizado com o backend para evitar fraude.
// Exemplo futuro:
// - Backend salva horário de início.
// - Front consulta o status da chamada.
// - Backend calcula o valor final pelo tempo real.
const timer = document.getElementById("callTimer");
const value = document.getElementById("callValue");

if (timer && value) {
  let seconds = 0;
  const pricePerMinute = 5.00;

  setInterval(() => {
    seconds += 1;

    const h = String(Math.floor(seconds / 3600)).padStart(2, "0");
    const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
    const s = String(seconds % 60).padStart(2, "0");

    timer.textContent = `${h}:${m}:${s}`;

    const total = (seconds / 60) * pricePerMinute;
    value.textContent = `R$ ${total.toFixed(2)}`;
  }, 1000);
}


// Cadastro: mostra campos de especialista somente quando "Sou especialista" estiver selecionado.
const accountTypeInputs = document.querySelectorAll('input[name="account_type"]');
const specialistFields = document.querySelector(".specialist-fields");

function updateSpecialistFields() {
  if (!accountTypeInputs.length || !specialistFields) return;

  const selected = document.querySelector('input[name="account_type"]:checked');
  const isSpecialist = selected && selected.value === "specialist";

  specialistFields.style.display = isSpecialist ? "block" : "none";

  document.querySelectorAll(".tab-option").forEach((option) => {
    const input = option.querySelector('input[name="account_type"]');
    option.classList.toggle("active", input && input.checked);
  });
}

accountTypeInputs.forEach((input) => {
  input.addEventListener("change", updateSpecialistFields);
});

updateSpecialistFields();


// Modal complementar por perfil: cliente paga, especialista recebe.
const flowModals = document.querySelectorAll(".flow-modal-backdrop");

flowModals.forEach((modal) => {
  modal.querySelectorAll("[data-close-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      modal.classList.add("is-hidden");
    });
  });
});

// Dropdown customizado para selects com data-apple-select
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("select[data-apple-select]").forEach((select) => {
    if (select.dataset.appleSelectReady === "true") return;

    select.dataset.appleSelectReady = "true";
    select.classList.add("apple-select-native");

    const wrapper = document.createElement("div");
    wrapper.className = "apple-select-wrapper";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "apple-select-button";
    button.textContent = select.options[select.selectedIndex]?.text || "Selecione";

    const menu = document.createElement("div");
    menu.className = "apple-select-menu";

    Array.from(select.options).forEach((option) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "apple-select-option";
      item.textContent = option.text;
      item.dataset.value = option.value;

      if (option.selected) {
        item.classList.add("active");
      }

      item.addEventListener("click", () => {
        select.value = option.value;
        button.textContent = option.text;

        menu.querySelectorAll(".apple-select-option").forEach((el) => {
          el.classList.remove("active");
        });

        item.classList.add("active");
        wrapper.classList.remove("open");

        select.dispatchEvent(new Event("change", { bubbles: true }));
      });

      menu.appendChild(item);
    });

    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);
    wrapper.appendChild(button);
    wrapper.appendChild(menu);

    button.addEventListener("click", () => {
      document.querySelectorAll(".apple-select-wrapper.open").forEach((openWrapper) => {
        if (openWrapper !== wrapper) {
          openWrapper.classList.remove("open");
        }
      });

      wrapper.classList.toggle("open");
    });
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".apple-select-wrapper")) {
      document.querySelectorAll(".apple-select-wrapper.open").forEach((wrapper) => {
        wrapper.classList.remove("open");
      });
    }
  });
});

// Modais internos das páginas do especialista
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-open-specialist-modal]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      const modalName = button.getAttribute("data-open-specialist-modal");
      const modal = document.querySelector(`[data-specialist-modal="${modalName}"]`);

      if (modal) {
        modal.classList.add("is-open");
      }
    });
  });

  document.querySelectorAll("[data-close-specialist-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      button.closest(".specialist-modal-backdrop")?.classList.remove("is-open");
    });
  });

  document.querySelectorAll(".specialist-modal-backdrop").forEach((backdrop) => {
    backdrop.addEventListener("click", (event) => {
      if (event.target === backdrop) {
        backdrop.classList.remove("is-open");
      }
    });
  });
});

// Abas dentro dos modais do especialista
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-specialist-tab]").forEach((tab) => {
    tab.addEventListener("click", () => {
      const modal = tab.closest(".specialist-modal");
      const target = tab.getAttribute("data-specialist-tab");

      if (!modal || !target) return;

      modal.querySelectorAll("[data-specialist-tab]").forEach((item) => {
        item.classList.remove("active");
      });

      modal.querySelectorAll("[data-specialist-tab-panel]").forEach((panel) => {
        panel.classList.remove("active");
      });

      tab.classList.add("active");

      const targetPanel = modal.querySelector(`[data-specialist-tab-panel="${target}"]`);
      if (targetPanel) {
        targetPanel.classList.add("active");
      }
    });
  });
});

// Seleção de plano pelos cards no modal de assinatura
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-plan-option]").forEach((card) => {
    card.addEventListener("click", () => {
      const modal = card.closest(".specialist-modal");
      const selectedPlan = card.getAttribute("data-plan-option");
      const hiddenInput = modal?.querySelector("#plano_desejado");

      if (!modal || !selectedPlan || !hiddenInput) return;

      modal.querySelectorAll("[data-plan-option]").forEach((item) => {
        item.classList.remove("active");
      });

      card.classList.add("active");
      hiddenInput.value = selectedPlan;
    });
  });
});

// Editor de tags do perfil especialista
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-tag-editor]").forEach((editor) => {
    const list = editor.querySelector("[data-tag-list]");
    const input = editor.querySelector("[data-tag-input]");
    const addButton = editor.querySelector("[data-add-tag]");
    const hidden = editor.querySelector("[data-tags-hidden]");

    if (!list || !input || !addButton || !hidden) return;

    let tags = hidden.value
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean);

    function syncTags() {
      hidden.value = tags.join(", ");
    }

    function renderTags() {
      list.innerHTML = "";

      tags.forEach((tag, index) => {
        const chip = document.createElement("span");
        chip.className = "tag-chip-edit";
        chip.textContent = tag;

        const remove = document.createElement("button");
        remove.type = "button";
        remove.textContent = "×";
        remove.setAttribute("aria-label", `Remover ${tag}`);

        remove.addEventListener("click", () => {
          tags.splice(index, 1);
          syncTags();
          renderTags();
        });

        chip.appendChild(remove);
        list.appendChild(chip);
      });

      syncTags();
    }

    function addTag() {
      const value = input.value.trim();

      if (!value) return;

      const exists = tags.some((tag) => tag.toLowerCase() === value.toLowerCase());

      if (!exists) {
        tags.push(value);
      }

      input.value = "";
      syncTags();
      renderTags();
    }

    addButton.addEventListener("click", addTag);

    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        addTag();
      }
    });

    renderTags();
  });
});

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".profile-photo-auto-form input[type='file']").forEach((input) => {
    input.addEventListener("change", () => {
      if (input.files && input.files.length > 0) {
        input.closest("form").submit();
      }
    });
  });
});

/* Foto do perfil - fluxo final único */
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.querySelector("[data-profile-photo-modal]");
  if (!modal || modal.dataset.photoReady === "true") return;

  modal.dataset.photoReady = "true";

  const title = modal.querySelector("[data-photo-modal-title]");
  const subtitle = modal.querySelector("[data-photo-modal-subtitle]");

  const titles = {
    view: ["Foto do perfil", "Veja a foto atual ou envie uma nova imagem para o perfil público."],
    update: ["Atualizar foto", "Escolha uma imagem, ajuste o enquadramento e salve."],
    delete: ["Excluir foto", "A exclusão definitiva será conectada ao backend depois."]
  };

  function setPanel(panelName) {
    modal.querySelectorAll("[data-photo-panel]").forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.photoPanel === panelName);
    });

    if (title && subtitle && titles[panelName]) {
      title.textContent = titles[panelName][0];
      subtitle.textContent = titles[panelName][1];
    }
  }

  document.querySelectorAll("[data-open-profile-photo-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      modal.classList.add("active");
      document.body.classList.add("modal-open");
      setPanel("view");
    });
  });

  modal.querySelectorAll("[data-close-profile-photo-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      modal.classList.remove("active");
      document.body.classList.remove("modal-open");
      setPanel("view");
    });
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.classList.remove("active");
      document.body.classList.remove("modal-open");
      setPanel("view");
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains("active")) {
      modal.classList.remove("active");
      document.body.classList.remove("modal-open");
      setPanel("view");
    }
  });

  modal.querySelectorAll("[data-photo-panel-button]").forEach((button) => {
    button.addEventListener("click", () => {
      setPanel(button.dataset.photoPanelButton);
    });
  });

  const form = modal.querySelector("[data-photo-crop-form]");
  const input = modal.querySelector("[data-photo-crop-input]");
  const preview = modal.querySelector("[data-photo-crop-preview]");
  const zoom = modal.querySelector("[data-photo-zoom]");
  const positionY = modal.querySelector("[data-photo-position-y]");
  const saveButton = modal.querySelector("[data-photo-save-crop]");

  if (!form || !input || !preview || !zoom || !positionY || !saveButton) return;

  let selectedFile = null;
  let previewImage = preview.querySelector("img");
  let previewNaturalWidth = previewImage ? previewImage.naturalWidth || 1 : 1;
  let previewNaturalHeight = previewImage ? previewImage.naturalHeight || 1 : 1;

  saveButton.disabled = true;
  saveButton.classList.add("disabled");

  function getPreviewSize() {
    const rect = preview.getBoundingClientRect();
    return {
      width: rect.width || 120,
      height: rect.height || 120
    };
  }

  function updateVerticalLimits() {
    if (!previewImage || !previewNaturalWidth || !previewNaturalHeight) return;

    const container = getPreviewSize();
    const currentZoom = Number(zoom.value);

    const baseScale = Math.max(
      container.width / previewNaturalWidth,
      container.height / previewNaturalHeight
    );

    const renderedHeight = previewNaturalHeight * baseScale * currentZoom;
    const maxOffset = Math.max(0, (renderedHeight - container.height) / 2);

    positionY.min = String(Math.round(-maxOffset));
    positionY.max = String(Math.round(maxOffset));

    let currentValue = Number(positionY.value);
    if (currentValue < -maxOffset) currentValue = -maxOffset;
    if (currentValue > maxOffset) currentValue = maxOffset;

    positionY.value = String(Math.round(currentValue));
  }

  function applyPreviewTransform() {
    if (!previewImage) return;

    updateVerticalLimits();

    previewImage.style.transform = `translateY(${Number(positionY.value)}px) scale(${Number(zoom.value)})`;
  }

  input.addEventListener("change", () => {
    if (!input.files || input.files.length === 0) return;

    selectedFile = input.files[0];
    const url = URL.createObjectURL(selectedFile);

    preview.innerHTML = "";

    previewImage = document.createElement("img");
    previewImage.src = url;
    previewImage.alt = "Prévia da foto";
    preview.appendChild(previewImage);

    previewImage.onload = () => {
      previewNaturalWidth = previewImage.naturalWidth || 1;
      previewNaturalHeight = previewImage.naturalHeight || 1;

      zoom.value = "1";
      positionY.value = "0";

      saveButton.disabled = false;
      saveButton.classList.remove("disabled");

      applyPreviewTransform();
    };
  });

  zoom.addEventListener("input", applyPreviewTransform);
  positionY.addEventListener("input", applyPreviewTransform);

  modal.querySelectorAll("[data-photo-range-step]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = button.dataset.photoRangeStep;
      const step = Number(button.dataset.step || 0);

      if (target === "zoom") {
        const next = Math.min(
          Number(zoom.max),
          Math.max(Number(zoom.min), Number(zoom.value) + step)
        );

        zoom.value = next.toFixed(2);
        applyPreviewTransform();
      }

      if (target === "vertical") {
        const next = Math.min(
          Number(positionY.max),
          Math.max(Number(positionY.min), Number(positionY.value) + step)
        );

        positionY.value = String(Math.round(next));
        applyPreviewTransform();
      }
    });
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!selectedFile || !previewImage) return;

    const canvas = document.createElement("canvas");
    const size = 600;

    canvas.width = size;
    canvas.height = size;

    const ctx = canvas.getContext("2d");
    const img = new Image();

    img.onload = () => {
      const currentZoom = Number(zoom.value);
      const baseScale = Math.max(size / img.width, size / img.height);
      const finalScale = baseScale * currentZoom;

      const drawWidth = img.width * finalScale;
      const drawHeight = img.height * finalScale;

      const maxCanvasOffset = Math.max(0, (drawHeight - size) / 2);
      const requestedOffset = Number(positionY.value) * (size / getPreviewSize().height);
      const safeOffset = Math.min(maxCanvasOffset, Math.max(-maxCanvasOffset, requestedOffset));

      const dx = (size - drawWidth) / 2;
      const dy = (size - drawHeight) / 2 + safeOffset;

      ctx.fillStyle = "#f8fafc";
      ctx.fillRect(0, 0, size, size);
      ctx.drawImage(img, dx, dy, drawWidth, drawHeight);

      canvas.toBlob((blob) => {
        if (!blob) return;

        const formData = new FormData();
        formData.append("foto_perfil", blob, "foto_perfil.png");

        fetch("/especialista/perfil/foto", {
          method: "POST",
          body: formData
        }).then(() => {
          window.location.href = "/especialista/perfil";
        });
      }, "image/png", 0.92);
    };

    img.src = URL.createObjectURL(selectedFile);
  });
});
