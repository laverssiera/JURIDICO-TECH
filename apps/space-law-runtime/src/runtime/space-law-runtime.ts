type OrbitalMissionPayload = {
  mission: string
  vehicle?: string
  launch_country?: string
  destination?: "leo" | "geo" | "lunar" | "martian" | "deep-space"
  involves_dual_use_tech?: boolean
  includes_us_munitions_list_item?: boolean
  includes_us_origin_hardware?: boolean
  has_reexport?: boolean
  destination_country?: string
  end_user_verified?: boolean
}

export class SpaceLawRuntime {
  async validateMarsOperation() {
    return {
      treaty_compliance: true,
      planetary_protection: true,
      exploration_authorized: true
    }
  }

  async validateOrbitalResearch() {
    return {
      orbital_clearance: true,
      scientific_operation: "approved"
    }
  }

  async validateOuterSpaceTreatyRuntime(payload: OrbitalMissionPayload) {
    const militaryUseRisk = payload.involves_dual_use_tech === true

    return {
      runtime: "outer-space-treaty",
      mission: payload.mission,
      non_appropriation: true,
      peaceful_use: !militaryUseRisk,
      liability_framework_ready: true,
      status: militaryUseRisk ? "review-required" : "compliant"
    }
  }

  async validateItarRuntime(payload: OrbitalMissionPayload) {
    const hasItarControlledItem = payload.includes_us_munitions_list_item === true
    const needsLicense = hasItarControlledItem || payload.has_reexport === true

    return {
      runtime: "itar",
      mission: payload.mission,
      usml_item_detected: hasItarControlledItem,
      license_required: needsLicense,
      destination_country: payload.destination_country ?? "undisclosed",
      status: needsLicense ? "license-required" : "compliant"
    }
  }

  async validateExportControlRuntime(payload: OrbitalMissionPayload) {
    const hasUsOriginHardware = payload.includes_us_origin_hardware === true
    const endUserVerified = payload.end_user_verified !== false
    const hasReexport = payload.has_reexport === true
    const needsEscalation = (hasUsOriginHardware && hasReexport) || !endUserVerified

    return {
      runtime: "export-control",
      mission: payload.mission,
      end_user_verified: endUserVerified,
      reexport_detected: hasReexport,
      eccn_review_required: hasUsOriginHardware,
      status: needsEscalation ? "escalation-required" : "compliant"
    }
  }

  async validateMissionCompliance(payload: OrbitalMissionPayload) {
    const outerSpaceTreaty = await this.validateOuterSpaceTreatyRuntime(payload)
    const itar = await this.validateItarRuntime(payload)
    const exportControl = await this.validateExportControlRuntime(payload)

    const requiresReview =
      outerSpaceTreaty.status !== "compliant" ||
      itar.status !== "compliant" ||
      exportControl.status !== "compliant"

    return {
      mission: payload.mission,
      runtime_suite: ["space-law", "outer-space-treaty", "itar", "export-control"],
      requires_review: requiresReview,
      controls: {
        outer_space_treaty: outerSpaceTreaty,
        itar,
        export_control: exportControl
      }
    }
  }
}