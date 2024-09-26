function deleteGift(giftId) {
  fetch("/delete-gift", {
    method: "POST",
    body: JSON.stringify({ giftId: giftId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}
