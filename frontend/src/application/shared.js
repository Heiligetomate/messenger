
const userNameKey = "tomate-username";
const passwordKey = "tomate-password";

export function getFromStorage(isUsername){
  let key = isUsername ? userNameKey : passwordKey;
  try{
    return sessionStorage.getItem(key);
  } catch(_) {
    sessionStorage.setItem(key, "")
    return sessionStorage.getItem(key);
  }
}

export function save(isUsername, value){
  let key = isUsername ? userNameKey : passwordKey;
  sessionStorage.setItem(key, value);
}


