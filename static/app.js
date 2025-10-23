document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("recipeForm");
    const recipesContainer = document.getElementById("recipes");

    function loadRecipes() {
        fetch("/api/recipes")
            .then(res => res.json())
            .then(data => {
                recipesContainer.innerHTML = "";
                data.forEach(recipe => {
                    const card = document.createElement("div");
                    card.className = "recipe-card";
                    card.innerHTML = `
                        <h3>${recipe.title}</h3>
                        <p><b>Тип:</b> ${recipe.meal_type}</p>
                        <p><b>Ингредиенты:</b> ${recipe.ingredients}</p>
                        <p><b>Инструкции:</b> ${recipe.instructions}</p>
                        ${recipe.image_url ? `<img src="${recipe.image_url}" alt="${recipe.title}">` : ""}
                    `;
                    recipesContainer.appendChild(card);
                });
            });
    }

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const formData = new FormData(form);

        fetch("/api/recipes", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(() => {
            form.reset();
            loadRecipes();
        });
    });

    loadRecipes();
});
