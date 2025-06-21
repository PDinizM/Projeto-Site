document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("reportForm");
    if (!form) return;

    const elements = {
        empresa: form.querySelector("#id_codigo_empresa"),
        balancete_normal: form.querySelector("#id_balancete_tipo_0"),
        balancete_referencial: form.querySelector("#id_balancete_tipo_1"),
        cruzamento_ecf: form.querySelector("#id_cruzamento_ecf"),
        consolidado: form.querySelector("#id_consolidado"),
        emitir_varias_empresas: form.querySelector("#id_emitir_varias_empresas"),
        helpMultiplasEmpresas: form.querySelector("#help-multiplas-empresas"),
    };

    const filterSingleCompany = (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
    };

    const filterMultiCompany = (e) => {
        let valor = e.target.value;
        valor = valor.replace(/[^0-9,]/g, '');
        valor = valor.replace(/^,/, '');
        valor = valor.replace(/,+/g, ',');
        e.target.value = valor;
    };

    const updateEmpresaFieldAttributes = (state) => {
        if (!elements.empresa) return;

        const allowMultiple = state.consolidado || state.emitir_varias_empresas;

        elements.empresa.removeEventListener("input", filterSingleCompany);
        elements.empresa.removeEventListener("input", filterMultiCompany);

        if (allowMultiple) {
            elements.empresa.maxLength = 255;
            elements.empresa.pattern = "^[0-9,]*[0-9]$";
            elements.empresa.title = "Digite códigos de empresa separados por vírgula.";
            elements.empresa.placeholder = "Ex: 1,2,3"; 
            elements.empresa.addEventListener("input", filterMultiCompany);
        } else {
            elements.empresa.maxLength = 7;
            elements.empresa.pattern = "^[0-9]+$";
            elements.empresa.title = "Digite apenas um código com até 7 números.";
            elements.empresa.placeholder = "Digite apenas números";
            elements.empresa.addEventListener("input", filterSingleCompany);
        }
        
        if (elements.helpMultiplasEmpresas) {
            elements.helpMultiplasEmpresas.classList.toggle('d-none', !allowMultiple);
        }

        if (elements.empresa.dataset.lastMode !== String(allowMultiple)) {
            elements.empresa.value = "";
        }
        elements.empresa.dataset.lastMode = String(allowMultiple);
    };
    

    const handleSpecialLogic = (state) => {

        if (state.balancete_referencial && elements.cruzamento_ecf?.checked) {

            elements.cruzamento_ecf.checked = false;
            state.cruzamento_ecf = false; 
        }
    };

    const evaluateVisibilityRule = (rule, state) => {
        const conditions = rule.split(' ');

        return conditions.every(condition => {
            const isNegative = condition.startsWith('!');
            const key = isNegative ? condition.substring(1) : condition;

            if (isNegative) {
                return !state[key];
            } else {

                return state[key];
            }
        });
    };

    const updateFormState = () => {
        const state = {
            balancete_normal: elements.balancete_normal?.checked || false,
            balancete_referencial: elements.balancete_referencial?.checked || false,
            cruzamento_ecf: elements.cruzamento_ecf?.checked || false,
            consolidado: elements.consolidado?.checked || false,
            emitir_varias_empresas: elements.emitir_varias_empresas?.checked || false,
        };

        handleSpecialLogic(state);

        form.querySelectorAll("[data-show-when]").forEach(element => {
            const rule = element.getAttribute("data-show-when");
            const shouldBeVisible = evaluateVisibilityRule(rule, state);
            element.classList.toggle("d-none", !shouldBeVisible);
            
            if (!shouldBeVisible && !element.id.includes('help')) {
                const input = element.querySelector('input[type="checkbox"]');
                if (input) input.checked = false;
            }
        });
        
        updateEmpresaFieldAttributes(state);
    };

    form.addEventListener("change", updateFormState);
    form.addEventListener("reset", () => {
        setTimeout(updateFormState, 0);
    });
    updateFormState();
});
