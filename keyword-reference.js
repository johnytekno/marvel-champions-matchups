const KEYWORD_REFERENCE = [
  {name:"Alliance",category:"Player card",summary:"When you announce an Alliance card, any players may contribute resources toward its costs. Only the player playing it resolves the card."},
  {name:"Assault",category:"Scheme",summary:"For a basic thwart against an Assault scheme, use the character's ATK instead of THW. An ally also takes its ATK consequential damage."},
  {name:"Form",category:"Identity",summary:"Grants an identity an additional named form with its own change conditions. Changing that extra form does not use the normal hero/alter-ego flip."},
  {name:"Guard",category:"Minion",summary:"While this minion is engaged with you, cards you control cannot attack the villain."},
  {name:"Hinder X",category:"Scheme",summary:"This card enters play with X additional threat, on top of any threat it would normally receive."},
  {name:"Incite X",category:"Encounter",summary:"When this card is revealed, place X threat on the main scheme."},
  {name:"Linked (Card Title)",category:"Deckbuilding",summary:"Do not put this card in a deck. Set it aside during setup when the named card is included; that named card brings it into the game."},
  {name:"Overkill",category:"Attack",summary:"If the attack defeats an ally, excess damage hits its controller's identity. If it defeats a minion, excess damage hits the villain."},
  {name:"Patrol",category:"Minion",summary:"While this minion is engaged with you, cards you control cannot thwart the main scheme. Side schemes remain valid targets."},
  {name:"Peril",category:"Encounter",summary:"Resolve this card alone: you cannot consult the table, and other players cannot play cards or trigger abilities to help."},
  {name:"Permanent",category:"Setup",summary:"This card starts set aside. Once in play, effects outside its own set cannot defeat it, remove it, or blank its text."},
  {name:"Piercing",category:"Attack",summary:"Before this attack deals damage, discard every Tough status from the target. If the attack would deal no damage, Piercing removes nothing."},
  {name:"Quickstrike",category:"Minion",summary:"After this minion engages a player in hero form, it attacks that player. Its When Revealed ability resolves first if it was revealed."},
  {name:"Ranged",category:"Attack",summary:"This attack ignores the Retaliate keyword."},
  {name:"Requirement (Resources)",category:"Player card",summary:"You cannot play this card unless every listed resource type is spent toward its cost. Ignoring the resource cost does not bypass the requirement."},
  {name:"Restricted",category:"Player card",summary:"You may control at most two Restricted cards. If you ever control more, immediately discard Restricted cards until only two remain."},
  {name:"Retaliate X",category:"Character",summary:"After this character is attacked, it deals X damage to the attacker, provided the retaliating character is still in play."},
  {name:"Setup",category:"Setup",summary:"This card begins the game in play and enters during the Put Setup Cards Into Play step."},
  {name:"Stalwart",category:"Status",summary:"This character cannot be stunned or confused. If it gains Stalwart, remove any Stunned and Confused status cards already on it."},
  {name:"Steady",category:"Status",summary:"This character needs two Stunned cards to be stunned or two Confused cards to be confused. When one cancels an activation, remove all of that type."},
  {name:"Surge",category:"Encounter",summary:"When revealed, deal yourself one facedown encounter card. Finish the current card and its responses before revealing the added card later in the queue."},
  {name:"Team-Up",category:"Deckbuilding",summary:"Your identity must match one named character to include this card. Both named friendly characters must be in play before you can play it."},
  {name:"Teamwork (Trait)",category:"Minion",summary:"After this minion enters play and engages, it activates if another minion with the named trait is in play. Resolve its When Revealed ability first."},
  {name:"Temporary",category:"Card state",summary:"Discard this card from play when the round ends."},
  {name:"Toughness",category:"Character",summary:"After this character enters play, give it a Tough status card."},
  {name:"Uses (X type)",category:"Player card",summary:"This card enters with X all-purpose counters of the named type. Its abilities spend them; discard the card after the final counter is removed and that effect resolves."},
  {name:"Victory X",category:"Victory display",summary:"When this card meets its listed defeat or discard condition, place it in the shared victory display instead of the discard pile. X is its victory value."},
  {name:"Villainous",category:"Enemy",summary:"When this character uses a basic power, give it a facedown boost card; resolve the boost ability and icons with that power, then discard the boost card."},
];

globalThis.MC_KEYWORDS = KEYWORD_REFERENCE;

const keywordEscape = value => String(value).replace(/[&<>"']/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[character]));

function keywordMatches(keyword, query) {
  const normalized = query.trim().toLowerCase();
  return !normalized || `${keyword.name} ${keyword.category} ${keyword.summary}`.toLowerCase().includes(normalized);
}

function renderKeywordReference(query = "") {
  const grid = document.querySelector("#keywordGrid");
  const count = document.querySelector("#keywordCount");
  const matches = KEYWORD_REFERENCE.filter(keyword => keywordMatches(keyword, query));
  count.textContent = query.trim() ? `${matches.length} of ${KEYWORD_REFERENCE.length} keywords` : `${KEYWORD_REFERENCE.length} keywords`;
  grid.innerHTML = matches.length
    ? matches.map(keyword => `<article class="keyword-card"><div class="keyword-card-head"><h3>${keywordEscape(keyword.name)}</h3><span>${keywordEscape(keyword.category)}</span></div><p>${keywordEscape(keyword.summary)}</p></article>`).join("")
    : `<div class="keyword-empty"><strong>No keyword found.</strong><span>Try a rule effect such as threat, status, minion, attack, or setup.</span></div>`;
}

document.addEventListener("DOMContentLoaded", () => {
  const openButton = document.querySelector("#keywordReference");
  const dialog = document.querySelector("#keywordDialog");
  const closeButton = document.querySelector("#keywordClose");
  const search = document.querySelector("#keywordSearch");

  renderKeywordReference();
  openButton.addEventListener("click", () => {
    search.value = "";
    renderKeywordReference();
    dialog.showModal();
    requestAnimationFrame(() => search.focus());
  });
  closeButton.addEventListener("click", () => dialog.close());
  search.addEventListener("input", event => renderKeywordReference(event.target.value));
  dialog.addEventListener("click", event => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", () => openButton.focus());
});
