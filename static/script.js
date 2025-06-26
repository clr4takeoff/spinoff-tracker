function copyPhones(id) {
    const phoneText = document.getElementById(id).innerText.trim();
    if (!phoneText) {
        alert("복사할 전화번호가 없습니다.");
        return;
    }
    navigator.clipboard.writeText(phoneText)
        .then(() => alert("전화번호가 복사되었습니다!"))
        .catch(err => alert("복사 실패: " + err));
}

function loadAndCopyText(sectionId) {
    const filePath = sectionId === 'finishedPhones'
        ? '/static/finished_text.json'
        : '/static/texts.json';

    fetch(filePath)
        .then(response => response.json())
        .then(data => {
            const text = data[sectionId] || "복사할 텍스트 없음";
            navigator.clipboard.writeText(text)
                .then(() => alert("텍스트가 복사되었습니다!"))
                .catch(err => alert("복사 실패: " + err));
        });
}
