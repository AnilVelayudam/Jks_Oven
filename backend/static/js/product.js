// PRICE UPDATE
function getSelectedWeight() {
    let selected = document.querySelector('input[name="weight"]:checked');
    let custom = document.getElementById("customWeight");

    if (custom && custom.value) {
        return parseFloat(custom.value);
    }

    return selected ? parseFloat(selected.value) : 1;
}

function getSelectedCream() {
    let cream = document.querySelector('input[name="cream"]:checked');
    return cream ? cream.value : "whipping";
}

function updatePrice(){
    let cream = getSelectedCream();
    let weight = getSelectedWeight();

    let basePrice = basePrices[cream];

    if(basePrice === null){
        document.getElementById("price").innerText = "Not Available";
        return;
    }

    let finalPrice = basePrice * weight;
    document.getElementById("price").innerText = "₹" + finalPrice.toFixed(0);
}


// INIT
document.addEventListener("DOMContentLoaded", function(){

updatePrice();

document.querySelectorAll('input[name="cream"]').forEach(el => {
    el.addEventListener("change", updatePrice);
});

document.querySelectorAll('input[name="weight"]').forEach(el => {
    el.addEventListener("change", () => {
        document.getElementById("customWeight").value = "";
        updatePrice();
    });
});

document.getElementById("customWeight").addEventListener("input", () => {
    document.querySelectorAll('input[name="weight"]').forEach(el => el.checked = false);
    updatePrice();
});
});


// ADD TO CART
function addToCart(){
    let cream = document.querySelector('input[name="cream"]:checked').value;
    let weight = getSelectedWeight();

    window.location.href = `/add-to-cart/${window.productId}/?cream=${cream}&weight=${weight}`;
}


// ORDER NOW
function orderNow(){
    let cream = document.querySelector('input[name="cream"]:checked').value;
    let weight = getSelectedWeight();

    window.location.href = `/buy-now/${window.productId}/?cream=${cream}&weight=${weight}`;
}


// IMAGE SWITCH
function changeImage(el){
    const main = document.getElementById("mainImage");
    main.src = el.src;

    document.querySelectorAll('.thumbnail-container img').forEach(img => {
        img.classList.remove('active');
    });

    el.classList.add('active');
}