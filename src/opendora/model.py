from __future__ import annotations

from sqlalchemy.orm import QueryableAttribute
from sqlmodel import SQLModel, Field
from datetime import date
from decimal import Decimal
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.currency_code import ISO4217
from enum import StrEnum
from typing import ClassVar, cast, Any


# Function to generate foreign key strings from columns
# Does not work with self-referencing foreign keys
def fk(col: Any) -> str:
    attr = cast(QueryableAttribute[Any], col)
    return f"{attr.class_.__tablename__}.{attr.key}"


# Regex patterns for data validation
LEI_PATTERN = r"^[0-9A-Z]{18}[0-9]{2}$"  # Legal Entity Identifier pattern


# Enumeration for entity types
class EntityType(StrEnum):
    BANK = "BANK"
    INSURANCE = "INSURANCE"
    INVESTMENT_FIRM = "INVESTMENT_FIRM"
    PAYMENT_INSTITUTION = "PAYMENT_INSTITUTION"
    ELECTRONIC_MONEY_INSTITUTION = "ELECTRONIC_MONEY_INSTITUTION"
    OTHER = "OTHER"


# Enumeration for criticality assessment
class CriticalityAssessment(StrEnum):
    CRITICAL = "CRITICAL"
    IMPORTANT = "IMPORTANT"
    NON_CRITICAL = "NON_CRITICAL"
    NON_IMPORTANT = "NON_IMPORTANT"


class RegisterMaintainer(SQLModel, table=True):
    """B.01.01 — Financial entity maintaining the register of information"""

    table_code: ClassVar[str] = "B.01.01"
    table_name: ClassVar[str] = (
        "Financial entity maintaining the register of information"
    )

    lei: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        title="0010",
        description="LEI of the entity maintaining the register of information",
    )
    name: str = Field(max_length=255, title="0020", description="Name of the entity")
    country: CountryAlpha2 = Field(
        min_length=2, max_length=2, title="0030", description="Country of the entity"
    )
    type: str = Field(max_length=255, title="0040", description="Type of entity")
    competent_authority: str = Field(
        max_length=255, title="0050", description="Competent Authority"
    )
    reporting_date: date = Field(title="0060", description="Date of the reporting")


class RegisteredEntity(SQLModel, table=True):
    """B.01.02 — List of financial entities within the scope of the register of information"""

    table_code: ClassVar[str] = "B.01.02"
    table_name: ClassVar[str] = (
        "List of financial entities within the scope of the register of information"
    )

    lei: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        title="0010",
        description="LEI of the entity",
    )
    name: str = Field(max_length=255, title="0020", description="Name of the entity")
    country: CountryAlpha2 = Field(
        min_length=2, max_length=2, title="0030", description="Country of the entity"
    )
    type: str = Field(max_length=255, title="0040", description="Type of entity")
    hierarchy: str | None = Field(
        default=None,
        max_length=255,
        title="0050",
        description="Hierarchy of the entity within the group (where applicable)",
    )
    parent_lei: str | None = Field(
        default=None,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key="registeredentity.lei",
        title="0060",
        description="LEI of the direct parent undertaking of the financial entity",
    )
    last_update_date: date = Field(title="0070", description="Date of last update")
    integration_date: date = Field(
        title="0080", description="Date of integration in the Register of information"
    )
    deletion_date: date | None = Field(
        default=None,
        title="0090",
        description="Date of deletion in the Register of information",
    )
    currency: ISO4217 | None = Field(
        default=None, min_length=3, max_length=3, title="0100", description="Currency"
    )
    total_assets: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
        title="0110",
        description="Value of total assets - of the financial entity",
    )


class EntityBranch(SQLModel, table=True):
    """B.01.03 — List of branches"""

    table_code: ClassVar[str] = "B.01.03"
    table_name: ClassVar[str] = "List of branches"

    branch_code: str = Field(
        primary_key=True,
        max_length=255,
        title="0010",
        description="Identification code of the branch",
    )
    head_office_lei: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=fk(RegisteredEntity.lei),
        title="0020",
        description="LEI of the financial entity head office of the branch",
    )
    name: str = Field(max_length=255, title="0030", description="Name of the branch")
    country: CountryAlpha2 = Field(
        min_length=2, max_length=2, title="0040", description="Country of the branch"
    )


class ContractGeneral(SQLModel, table=True):
    """B.02.01 — Contractual Arrangements – General Information"""

    table_code: ClassVar[str] = "B.02.01"
    table_name: ClassVar[str] = "Contractual Arrangements – General Information"

    reference_number: str = Field(
        primary_key=True,
        max_length=255,
        title="0010",
        description="Contractual arrangement reference number",
    )
    type: str = Field(
        max_length=255, title="0020", description="Type of contractual arrangement"
    )
    overarching_reference_number: str | None = Field(
        default=None,
        max_length=255,
        foreign_key="contractgeneral.reference_number",
        title="0030",
        description="Overarching contractual arrangement reference number",
    )
    currency: ISO4217 = Field(
        min_length=3,
        max_length=3,
        title="0040",
        description="Currency of the amount reported",
    )
    annual_cost: Decimal = Field(
        decimal_places=2,
        title="0050",
        description="Annual expense or estimated cost of the contractual arrangement for the past year",
    )


class ContractSpecific(SQLModel, table=True):
    """B.02.02 — Contractual Arrangements – Specific information"""

    table_code: ClassVar[str] = "B.02.02"
    table_name: ClassVar[str] = "Contractual Arrangements – Specific information"

    reference_number: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=fk(ContractGeneral.reference_number),
        title="0010",
        description="Contractual arrangement reference number",
    )
    lei: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=fk(RegisteredEntity.lei),
        title="0020",
        description="LEI of the financial entity making use of the ICT service",
    )
    provider_code: str = Field(
        primary_key=True,
        max_length=255,
        title="0030",
        description="Identification code of the third-party service provider",
    )
    provider_code_type: str | None = Field(
        default=None,
        max_length=255,
        title="0040",
        description="Type of code to identify the third-party service provider",
    )
    function_identifier: str = Field(
        primary_key=True,
        max_length=255,
        title="0050",
        description="Function identifier",
    )
    service_type: str = Field(
        primary_key=True,
        max_length=255,
        title="0060",
        description="Type of ICT services",
    )
    start_date: date = Field(
        title="0070", description="Start date of the contractual arrangement"
    )
    end_date: date = Field(
        title="0080", description="End date of the contractual arrangement"
    )
    termination_reason: str | None = Field(
        default=None,
        max_length=255,
        title="0090",
        description="Reason of the termination or ending of the contractual arrangement",
    )
    client_notice_period: int | None = Field(
        default=None,
        title="0100",
        description="Notice period for the financial entity",
    )
    provider_notice_period: int | None = Field(
        default=None,
        title="0110",
        description="Notice period for the ICT third-party service provider",
    )
    governing_law_country: CountryAlpha2 | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        title="0120",
        description="Country of the governing law of the contractual arrangement",
    )
    service_country: CountryAlpha2 = Field(
        primary_key=True,
        min_length=2,
        max_length=2,
        title="0130",
        description="Country of provision of the ICT services",
    )
    data_storage: bool = Field(title="0140", description="Storage of data")
    data_at_rest_location: CountryAlpha2 = Field(
        primary_key=True,
        min_length=2,
        max_length=2,
        title="0150",
        description="Location of the data at rest (storage)",
    )
    data_processing_location: CountryAlpha2 = Field(
        primary_key=True,
        min_length=2,
        max_length=2,
        title="0160",
        description="Location of management of the data (processing)",
    )
    data_sensitivity: str | None = Field(
        default=None,
        max_length=255,
        title="0170",
        description="Sensitiveness of the data stored by the ICT third-party service provider",
    )
    service_reliance: str | None = Field(
        default=None,
        max_length=255,
        title="0180",
        description="Level of reliance on the ICT service supporting the critical or important function",
    )


class IntraGroupContract(SQLModel, table=True):
    """B.02.03 — List of intra-group contractual arrangements"""

    table_code: ClassVar[str] = "B.02.03"
    table_name: ClassVar[str] = "List of intra-group contractual arrangements"

    reference_number: str = Field(
        primary_key=True,
        max_length=255,
        title="0010",
        description="Contractual arrangement with ICT intra-group service provider",
    )
    linked_third_party_contract: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=fk(ContractGeneral.reference_number),
        title="0020",
        description="Linked contractual arrangement with ICT third-party service provider",
    )


class ContractReceiver(SQLModel, table=True):
    """B.03.01 — Entities signing the Contractual Arrangements for receiving ICT service(s) or on behalf of the entities making use of the ICT service(s)"""

    table_code: ClassVar[str] = "B.03.01"
    table_name: ClassVar[str] = (
        "Entities signing the Contractual Arrangements for receiving ICT service(s) or on behalf of the entities making use of the ICT service(s)"
    )

    reference_number: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=fk(ContractGeneral.reference_number),
        title="0010",
        description="Contractual arrangement reference number",
    )
    lei: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=fk(RegisteredEntity.lei),
        title="0020",
        description="LEI of the entity signing the contractual arrangement",
    )


class ContractProvider(SQLModel, table=True):
    """B.03.02 — Third-party service providers signing the Contractual Arrangements for providing ICT service(s)"""

    table_code: ClassVar[str] = "B.03.02"
    table_name: ClassVar[str] = (
        "Third-party service providers signing the Contractual Arrangements for providing ICT service(s)"
    )

    reference_number: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=fk(ContractGeneral.reference_number),
        title="0010",
        description="Contractual arrangement reference number",
    )
    provider_code: str = Field(
        primary_key=True,
        max_length=255,
        title="0020",
        description="Identification code of the third-party service provider",
    )
    provider_code_type: str | None = Field(
        default=None,
        max_length=255,
        title="0030",
        description="Type of code of the third-party service provider",
    )


class IntraGroupProvider(SQLModel, table=True):
    """B.03.03 — Entities signing the Contractual Arrangements for providing ICT service(s)"""

    table_code: ClassVar[str] = "B.03.03"
    table_name: ClassVar[str] = (
        "Entities signing the Contractual Arrangements for providing ICT service(s)"
    )

    reference_number: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=fk(ContractGeneral.reference_number),
        title="0010",
        description="Contractual arrangement reference number",
    )
    lei: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=fk(RegisteredEntity.lei),
        title="0020",
        description="LEI of the intra-group entity providing ICT service",
    )


class ServiceUser(SQLModel, table=True):
    """B.04.01 — Financial entities making use of the ICT services"""

    table_code: ClassVar[str] = "B.04.01"
    table_name: ClassVar[str] = "Financial entities making use of the ICT services"

    reference_number: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=fk(ContractGeneral.reference_number),
        title="0010",
        description="Contractual arrangement reference number",
    )
    lei: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=fk(RegisteredEntity.lei),
        title="0020",
        description="LEI of the financial entity",
    )
    is_branch: bool = Field(
        title="0030",
        description="Is the entity making use of the ICT services a branch of a financial entity?",
    )
    branch_code: str = Field(
        primary_key=True,
        max_length=255,
        title="0040",
        description="Identification code of the branch",
    )


class ThirdPartyProvider(SQLModel, table=True):
    """B.05.01 — ICT third-party service provider"""

    table_code: ClassVar[str] = "B.05.01"
    table_name: ClassVar[str] = "ICT third-party service provider"

    provider_code: str = Field(
        primary_key=True,
        max_length=255,
        title="0010",
        description="Identification code of the third-party service provider",
    )
    provider_code_type: str = Field(
        max_length=255,
        title="0020",
        description="Type of code of the third-party service provider",
    )
    additional_code: int | None = Field(
        default=None,
        title="0030",
        description="Additional identification code of the third-party service provider",
    )
    additional_code_type: str | None = Field(
        default=None,
        max_length=255,
        title="0040",
        description="Type of additional identification code of the third-party service provider",
    )
    legal_name: str = Field(
        max_length=255,
        title="0050",
        description="Legal name of the third-party service provider",
    )
    name_in_latin_alphabet: str | None = Field(
        default=None,
        max_length=255,
        title="0060",
        description="Name of the ICT third-party service provider in Latin alphabet",
    )
    person_type: str = Field(
        max_length=255,
        title="0070",
        description="Type of person of the third-party service provider",
    )
    country_of_headquarters: CountryAlpha2 = Field(
        min_length=2,
        max_length=2,
        title="0080",
        description="Country of the third-party service provider's headquarters",
    )
    currency: ISO4217 | None = Field(
        default=None,
        min_length=3,
        max_length=3,
        title="0090",
        description="Currency of the amount reported",
    )
    annual_cost: Decimal | None = Field(
        default=None,
        decimal_places=2,
        title="0100",
        description="Total annual expense or estimated cost of the third-party service provider",
    )
    ultimate_parent_undertaking_provider_code: str = Field(
        max_length=255,
        title="0110",
        description="Identification code of the third-party service provider's ultimate parent undertaking",
    )
    ultimate_parent_undertaking_provider_code_type: str | None = Field(
        default=None,
        max_length=255,
        title="0120",
        description="Type of code of the third-party service provider's ultimate parent undertaking",
    )


class ServiceType(SQLModel, table=True):
    """Type of ICT Services reference table"""

    table_code: ClassVar[None] = None
    table_name: ClassVar[str] = "Type of ICT Services"

    identifier: str = Field(
        primary_key=True, max_length=50, description="Type of ICT services identifier"
    )
    name: str = Field(max_length=50, description="Type of ICT services name")
    description: str = Field(
        max_length=255, description="Type of ICT services description"
    )


class ServiceSupplyChain(SQLModel, table=True):
    """B.05.02 — ICT service supply chains"""

    table_code: ClassVar[str] = "B.05.02"
    table_name: ClassVar[str] = "ICT service supply chains"

    reference_number: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key="contractgeneral.reference_number",
        title="0010",
        description="Contractual arrangement reference number",
    )
    service_type: str = Field(
        primary_key=True,
        max_length=255,
        title="0020",
        foreign_key=fk(ServiceType.identifier),
        description="Type of ICT services",
    )
    provider_code: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=fk(ThirdPartyProvider.provider_code),
        title="0030",
        description="Identification code of the third-party service provider",
    )
    provider_code_type: str | None = Field(
        default=None,
        max_length=255,
        title="0040",
        description="Type of code of the third-party service provider",
    )
    rank: int = Field(primary_key=True, title="0050", description="Rank")
    recipient_code: str = Field(
        primary_key=True,
        max_length=255,
        title="0060",
        description="Identification code of the recipient of sub-contracted ICT services",
    )
    recipient_code_type: str | None = Field(
        default=None,
        max_length=255,
        title="0070",
        description="Type of code of the recipient of sub-contracted ICT services",
    )


class Function(SQLModel, table=True):
    """B.06.01 — Functions identification"""

    table_code: ClassVar[str] = "B.06.01"
    table_name: ClassVar[str] = "Functions identification"

    identifier: str = Field(
        primary_key=True,
        max_length=255,
        title="0010",
        description="Function identifier",
    )
    licensed_activity: str = Field(
        max_length=255, title="0020", description="Licenced activity"
    )
    function_name: str = Field(
        max_length=255, title="0030", description="Function name"
    )
    lei: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        foreign_key=fk(RegisteredEntity.lei),
        description="LEI of the financial entity",
    )
    assessment: str = Field(
        max_length=255, title="0040", description="Criticality or importance assessment"
    )
    reasons: str = Field(
        max_length=255,
        title="0050",
        description="Reasons for criticality or importance",
    )
    assessment_date: date = Field(
        title="0060",
        description="Date of the last assessment of criticality or importance",
    )
    recovery_time_objective: int = Field(
        title="0070", description="Recovery time objective of the function"
    )
    recovery_point_objective: int = Field(
        title="0080", description="Recovery point objective of the function"
    )
    impact_of_discontinuing: str = Field(
        max_length=255, title="0090", description="Impact of discontinuing the function"
    )


class ServiceAssessment(SQLModel, table=True):
    """B.07.01 — Assessment of the ICT services"""

    table_code: ClassVar[str] = "B.07.01"
    table_name: ClassVar[str] = "Assessment of the ICT services"

    reference_number: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=fk(ContractGeneral.reference_number),
        title="0010",
        description="Contractual arrangement reference number",
    )
    provider_code: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=fk(ThirdPartyProvider.provider_code),
        title="0020",
        description="Identification code of the third-party service provider",
    )
    provider_code_type: str = Field(
        max_length=255,
        title="0030",
        description="Type of code of the third-party service provider",
    )
    service_type: str = Field(
        primary_key=True,
        max_length=255,
        title="0040",
        foreign_key=fk(ServiceType.identifier),
        description="Type of ICT services",
    )
    provider_substitutability: str = Field(
        max_length=255,
        title="0050",
        description="Substitutability of the ICT third-party service provider",
    )
    non_substitutable_reason: str | None = Field(
        default=None,
        max_length=255,
        title="0060",
        description="Reason if the ICT third-party service provider is considered not substitutable or difficult to be substitutable",
    )
    last_audit_date: date = Field(
        title="0070",
        description="Date of the last audit on the ICT third-party service provider",
    )
    has_exit_plan: bool = Field(title="0080", description="Existence of an exit plan")
    possibility_of_reintegration: str = Field(
        max_length=255,
        title="0090",
        description="Possibility of reintegration of the contracted ICT service",
    )
    discontinuing_impact: str = Field(
        max_length=255,
        title="0100",
        description="Impact of discontinuing the ICT services",
    )
    alternative_provider_exists: bool = Field(
        title="0110",
        description="Are there alternative ICT third-party service providers identified?",
    )
    alternative_provider_details: str | None = Field(
        default=None,
        max_length=255,
        title="0120",
        description="Identification of alternative ICT TPP",
    )


def get_column_display_name(model_class: SQLModel, column_name: str) -> str:
    """Get the display name for a column from its description"""
    field = model_class.model_fields.get(column_name)
    if field and field.description:
        return field.description
    return column_name
