// File: web_app/static/js/components.js

// Toggle function for expandable cards
function toggleDetailCard(cardId) {
  const content = document.getElementById(cardId);
  const btn = content.previousElementSibling.querySelector(".expand-btn");

  content.classList.toggle("collapsed");
  btn.classList.toggle("expanded");
}

// Switch asset category tabs
function switchAssetCategory(category) {
  // Update tab buttons
  document.querySelectorAll(".category-tab").forEach((tab) => {
    tab.classList.remove("active");
  });
  document
    .querySelector(`[data-category="${category}"]`)
    .classList.add("active");

  // Update content
  document.querySelectorAll(".asset-category").forEach((cat) => {
    cat.classList.remove("active");
  });
  document.getElementById(category).classList.add("active");
}

// Populate world data
function populateWorldData(worldData) {
  if (!worldData) return;

  // Update world stats
  if (worldData.terrain) {
    const terrainEl = document.getElementById("terrainSize");
    if (terrainEl)
      terrainEl.textContent = `${worldData.terrain.size || "100x100"} units`;

    const biomeEl = document.getElementById("biomeType");
    if (biomeEl)
      biomeEl.textContent = worldData.terrain.biome || "Fantasy Forest";

    const elevationEl = document.getElementById("elevationRange");
    if (elevationEl)
      elevationEl.textContent = `${worldData.terrain.elevation_min || 0}-${
        worldData.terrain.elevation_max || 25
      }m`;

    const climateEl = document.getElementById("climate");
    if (climateEl)
      climateEl.textContent = worldData.terrain.climate || "Temperate";
  }

  // Update world description
  if (worldData.description) {
    const descEl = document.getElementById("worldDescription");
    if (descEl) descEl.textContent = worldData.description;
  }

  // Populate structures
  if (worldData.structures) {
    const structureGrid = document.getElementById("structureGrid");
    if (structureGrid) {
      structureGrid.innerHTML = worldData.structures
        .map(
          (structure) => `
                <div class="structure-item">
                    <span class="structure-icon">${
                      structure.icon || "🏗️"
                    }</span>
                    <div class="structure-name">${structure.name}</div>
                    <div class="structure-details">${
                      structure.description
                    }</div>
                </div>
            `
        )
        .join("");
    }
  }

  // Populate environment features
  if (worldData.environment_features) {
    const featuresContainer = document.getElementById("environmentFeatures");
    if (featuresContainer) {
      featuresContainer.innerHTML = worldData.environment_features
        .map(
          (feature) => `
                <span class="environment-tag">${feature}</span>
            `
        )
        .join("");
    }
  }
}

// Populate assets data
function populateAssetsData(assetsData) {
  if (!assetsData) return;

  // Update asset stats
  if (assetsData.stats) {
    const totalEl = document.querySelector(".stat-number");
    if (totalEl) totalEl.textContent = assetsData.stats.total || 47;
  }

  // Populate asset categories
  if (assetsData.categories) {
    Object.keys(assetsData.categories).forEach((categoryKey) => {
      const category = assetsData.categories[categoryKey];
      const container = document.querySelector(
        `#${categoryKey}-full .asset-grid`
      );

      if (container && category.assets) {
        container.innerHTML = category.assets
          .map(
            (asset) => `
                    <div class="asset-item">
                        <div class="asset-preview">${asset.icon || "📦"}</div>
                        <div class="asset-info">
                            <div class="asset-name">${asset.name}</div>
                            <div class="asset-type">${
                              asset.type || "Static Mesh"
                            }</div>
                            <div class="asset-files">
                                ${(asset.files || [])
                                  .map(
                                    (file) =>
                                      `<a href="/api/download-asset/${file}" class="file-link">${file}</a>`
                                  )
                                  .join("")}
                            </div>
                        </div>
                    </div>
                `
          )
          .join("");
      }
    });
  }
}

// Initialize components when page loads
document.addEventListener("DOMContentLoaded", function () {
  console.log("🎮 Components initialized");

  // Sample data for demonstration
  const sampleWorldData = {
    terrain: {
      size: "150x150",
      biome: "Mystical Forest",
      elevation_min: 0,
      elevation_max: 35,
      climate: "Magical Temperate",
    },
    description:
      "A mystical forest realm with ancient trees, crystal streams, and hidden magical clearings. The world features varied terrain including dense woodlands, open meadows, and mysterious caves.",
    structures: [
      {
        name: "Ancient Tavern",
        icon: "🏠",
        description: "Central gathering place with NPCs",
      },
      {
        name: "Mystic Blacksmith",
        icon: "⚒️",
        description: "Magical weapon crafting station",
      },
      {
        name: "Crystal Market",
        icon: "🏪",
        description: "Trading hub with rare goods",
      },
    ],
    environment_features: [
      "Ancient Oaks",
      "Crystal Streams",
      "Magical Clearings",
      "Hidden Caves",
      "Fairy Circles",
      "Stone Monuments",
    ],
  };

  const sampleAssetsData = {
    stats: {
      total: 73,
      blender_files: 15,
      textures: 28,
      materials: 12,
    },
    categories: {
      buildings: {
        assets: [
          {
            name: "Enchanted Tavern",
            type: "Building",
            icon: "🏠",
            files: ["tavern.blend", "tavern.glb"],
          },
          {
            name: "Mystic Forge",
            type: "Building",
            icon: "⚒️",
            files: ["forge.blend", "forge.glb"],
          },
          {
            name: "Crystal Tower",
            type: "Building",
            icon: "🗼",
            files: ["tower.blend", "tower.glb"],
          },
        ],
      },
    },
  };

  // Populate with sample data
  populateWorldData(sampleWorldData);
  populateAssetsData(sampleAssetsData);
});

// Function to update all component data when generation completes
function updateComponentData(generationData) {
  if (generationData.world) {
    populateWorldData(generationData.world);
  }
  if (generationData.assets) {
    populateAssetsData(generationData.assets);
  }
  // Add other component updates as needed
}

// Export functions for use in main app
window.toggleDetailCard = toggleDetailCard;
window.switchAssetCategory = switchAssetCategory;
window.populateWorldData = populateWorldData;
window.populateAssetsData = populateAssetsData;
window.updateComponentData = updateComponentData;
