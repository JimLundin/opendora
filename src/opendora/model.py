from sqlmodel import SQLModel, Field
from typing import Protocol
from datetime import date
from decimal import Decimal
from pydantic import field_validator, model_validator, ValidationInfo
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.currency_code import ISO4217
from enum import StrEnum


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


class B_01_01(SQLModel, table=True):
    """B.01.01 — Financial entity maintaining the register of information"""

    __table_code__ = "B.01.01"
    __table_display_name__ = "Financial entity maintaining the register of information"

    c0010: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        description="LEI of the entity maintaining the register of information",
    )
    c0020: str = Field(max_length=255, description="Name of the entity")
    c0030: CountryAlpha2 = Field(
        min_length=2, max_length=2, description="Country of the entity"
    )
    c0040: str = Field(max_length=255, description="Type of entity")
    c0050: str = Field(max_length=255, description="Competent Authority")
    c0060: date = Field(description="Date of the reporting")

    @field_validator("c0040")
    def validate_entity_type(cls, v: str) -> str:
        """Validate entity type"""
        # Check if the entity type is one of the standard types or a custom one
        try:
            return EntityType(v).value
        except ValueError:
            # If not a standard type, ensure it's not empty
            if not v.strip():
                raise ValueError("Entity type cannot be empty")
            return v


class B_01_02(SQLModel, table=True):
    """B.01.02 — List of financial entities within the scope of the register of information"""

    __table_code__ = "B.01.02"
    __table_display_name__ = (
        "List of financial entities within the scope of the register of information"
    )

    c0010: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        description="LEI of the entity",
    )
    c0020: str = Field(max_length=255, description="Name of the entity")
    c0030: CountryAlpha2 = Field(
        min_length=2, max_length=2, description="Country of the entity"
    )
    c0040: str = Field(max_length=255, description="Type of entity")
    c0050: str | None = Field(
        default=None,
        max_length=255,
        description="Hierarchy of the entity within the group (where applicable)",
    )
    c0060: str | None = Field(
        default=None,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=c0010,
        description="LEI of the direct parent undertaking of the financial entity",
    )
    c0070: date = Field(description="Date of last update")
    c0080: date = Field(
        description="Date of integration in the Register of information"
    )
    c0090: date | None = Field(
        default=None, description="Date of deletion in the Register of information"
    )
    c0100: ISO4217 | None = Field(
        default=None, min_length=3, max_length=3, description="Currency"
    )
    c0110: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
        description="Value of total assets - of the financial entity",
    )


class B_01_03(SQLModel, table=True):
    """B.01.03 — List of branches"""

    __table_code__ = "B.01.03"
    __table_display_name__ = "List of branches"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        description="Identification code of the branch",
    )
    c0020: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=B_01_02.c0010,
        description="LEI of the financial entity head office of the branch",
    )
    c0030: str = Field(max_length=255, description="Name of the branch")
    c0040: CountryAlpha2 = Field(
        min_length=2, max_length=2, description="Country of the branch"
    )


class B_02_01(SQLModel, table=True):
    """B.02.01 — Contractual Arrangements – General Information"""

    __table_code__ = "B.02.01"
    __table_display_name__ = "Contractual Arrangements – General Information"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        description="Contractual arrangement reference number",
    )
    c0020: str = Field(max_length=255, description="Type of contractual arrangement")
    c0030: str | None = Field(
        default=None,
        max_length=255,
        foreign_key=c0010,
        description="Overarching contractual arrangement reference number",
    )
    c0040: ISO4217 = Field(
        min_length=3, max_length=3, description="Currency of the amount reported"
    )
    c0050: Decimal = Field(
        decimal_places=2,
        description="Annual expense or estimated cost of the contractual arrangement for the past year",
    )


class B_02_02(SQLModel, table=True):
    """B.02.02 — Contractual Arrangements – Specific information"""

    __table_code__ = "B.02.02"
    __table_display_name__ = "Contractual Arrangements – Specific information"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_02_01.c0010,
        description="Contractual arrangement reference number",
    )
    c0020: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=B_01_02.c0010,
        description="LEI of the financial entity making use of the ICT service",
    )
    c0030: str = Field(
        primary_key=True,
        max_length=255,
        description="Identification code of the third-party service provider",
    )
    c0040: str | None = Field(
        default=None,
        max_length=255,
        description="Type of code to identify the third-party service provider",
    )
    c0050: str = Field(
        primary_key=True, max_length=255, description="Function identifier"
    )
    c0060: str = Field(
        primary_key=True, max_length=255, description="Type of ICT services"
    )
    c0070: date = Field(description="Start date of the contractual arrangement")
    c0080: date = Field(description="End date of the contractual arrangement")
    c0090: str | None = Field(
        default=None,
        max_length=255,
        description="Reason of the termination or ending of the contractual arrangement",
    )
    c0100: int | None = Field(
        default=None, description="Notice period for the financial entity"
    )
    c0110: int | None = Field(
        default=None,
        description="Notice period for the ICT third-party service provider",
    )
    c0120: CountryAlpha2 | None = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="Country of the governing law of the contractual arrangement",
    )
    c0130: CountryAlpha2 = Field(
        primary_key=True,
        min_length=2,
        max_length=2,
        description="Country of provision of the ICT services",
    )
    c0140: bool = Field(description="Storage of data")
    c0150: CountryAlpha2 = Field(
        primary_key=True,
        min_length=2,
        max_length=2,
        description="Location of the data at rest (storage)",
    )
    c0160: CountryAlpha2 = Field(
        primary_key=True,
        min_length=2,
        max_length=2,
        description="Location of management of the data (processing)",
    )
    c0170: str | None = Field(
        default=None,
        max_length=255,
        description="Sensitiveness of the data stored by the ICT third-party service provider",
    )
    c0180: str | None = Field(
        default=None,
        max_length=255,
        description="Level of reliance on the ICT service supporting the critical or important function",
    )


class B_02_03(SQLModel, table=True):
    """B.02.03 — List of intra-group contractual arrangements"""

    __table_code__ = "B.02.03"
    __table_display_name__ = "List of intra-group contractual arrangements"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        description="Contractual arrangement with ICT intra-group service provider",
    )
    c0020: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_02_01.c0010,
        description="Linked contractual arrangement with ICT third-party service provider",
    )


class B_03_01(SQLModel, table=True):
    """B.03.01 — Entities signing the Contractual Arrangements for receiving ICT service(s) or on behalf of the entities making use of the ICT service(s)"""

    __table_code__ = "B.03.01"
    __table_display_name__ = "Entities signing the Contractual Arrangements for receiving ICT service(s) or on behalf of the entities making use of the ICT service(s)"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_02_01.c0010,
        description="Contractual arrangement reference number",
    )
    c0020: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=B_01_02.c0010,
        description="LEI of the entity signing the contractual arrangement",
    )


class B_03_02(SQLModel, table=True):
    """B.03.02 — Third-party service providers signing the Contractual Arrangements for providing ICT service(s)"""

    __table_code__ = "B.03.02"
    __table_display_name__ = "Third-party service providers signing the Contractual Arrangements for providing ICT service(s)"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_02_01.c0010,
        description="Contractual arrangement reference number",
    )
    c0020: str = Field(
        primary_key=True,
        max_length=255,
        description="Identification code of the third-party service provider",
    )
    c0030: str | None = Field(
        default=None,
        max_length=255,
        description="Type of code of the third-party service provider",
    )


class B03_03(SQLModel, table=True):
    """B.03.03 — Entities signing the Contractual Arrangements for providing ICT service(s)"""

    __table_code__ = "B.03.03"
    __table_display_name__ = (
        "Entities signing the Contractual Arrangements for providing ICT service(s)"
    )

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_02_01.c0010,
        description="Contractual arrangement reference number",
    )
    c0020: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=B_01_02.c0010,
        description="LEI of the intra-group entity providing ICT service",
    )


class B_04_01(SQLModel, table=True):
    """B.04.01 — Financial entities making use of the ICT services"""

    __table_code__ = "B.04.01"
    __table_display_name__ = "Financial entities making use of the ICT services"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_02_01.c0010,
        description="Contractual arrangement reference number",
    )
    c0020: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        regex=LEI_PATTERN,
        foreign_key=B_01_02.c0010,
        description="LEI of the financial entity",
    )
    c0030: bool = Field(
        description="Is the entity making use of the ICT services a branch of a financial entity?"
    )
    c0040: str = Field(
        primary_key=True,
        max_length=255,
        description="Identification code of the branch",
    )

    @field_validator("c0010")
    def validate_arrangement_ref(cls, v: str) -> str:
        """Validate arrangement reference number format"""
        if not v or not v.strip():
            raise ValueError("Contractual arrangement reference number cannot be empty")
        return v

    @field_validator("c0040")
    def validate_branch_id(cls, v: str, info: ValidationInfo) -> str:
        """Validate branch ID based on the c0030 flag"""
        # Get values from the validation context
        values = info.data

        # If entity is a branch, branch ID must be provided
        if "c0030" in values and values["c0030"] is True:
            if not v or not v.strip():
                raise ValueError(
                    "Branch identification code is required when entity is a branch"
                )
        # If entity is not a branch, we could have a default code or empty value based on requirements
        # Here we'll use a placeholder value if not a branch
        elif "c0030" in values and values["c0030"] is False:
            if not v or not v.strip():
                return "NOT_APPLICABLE"  # Or could return a default value if preferred
        return v

    @model_validator(mode="after")
    def validate_entity_branch_consistency(self) -> "B_04_01":
        """Ensure consistency between branch flag and branch code"""
        if not self.c0030 and self.c0040 != "NOT_APPLICABLE" and self.c0040.strip():
            # If not a branch, but branch code is provided (and not our placeholder)
            raise ValueError(
                "Branch code should not be provided when entity is not a branch"
            )
        return self


class B_05_01(SQLModel, table=True):
    """B.05.01 — ICT third-party service provider"""

    __table_code__ = "B.05.01"
    __table_display_name__ = "ICT third-party service provider"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        description="Identification code of the third-party service provider",
    )
    c0020: str = Field(
        max_length=255, description="Type of code of the third-party service provider"
    )
    c0030: int | None = Field(
        default=None,
        description="Additional identification code of the third-party service provider",
    )
    c0040: str | None = Field(
        default=None,
        max_length=255,
        description="Type of additional identification code of the third-party service provider",
    )
    c0050: str = Field(
        max_length=255, description="Legal name of the third-party service provider"
    )
    c0060: str | None = Field(
        default=None,
        max_length=255,
        description="Name of the ICT third-party service provider in Latin alphabet",
    )
    c0070: str = Field(
        max_length=255, description="Type of person of the third-party service provider"
    )
    c0080: CountryAlpha2 = Field(
        min_length=2,
        max_length=2,
        description="Country of the third-party service provider's headquarters",
    )
    c0090: ISO4217 | None = Field(
        default=None,
        min_length=3,
        max_length=3,
        description="Currency of the amount reported",
    )
    c0100: Decimal | None = Field(
        default=None,
        decimal_places=2,
        description="Total annual expense or estimated cost of the third-party service provider",
    )
    c0110: str = Field(
        max_length=255,
        description="Identification code of the third-party service provider's ultimate parent undertaking",
    )
    c0120: str | None = Field(
        default=None,
        max_length=255,
        description="Type of code of the third-party service provider's ultimate parent undertaking",
    )


class B_05_02(SQLModel, table=True):
    """B.05.02 — ICT service supply chains"""

    __table_code__ = "B.05.02"
    __table_display_name__ = "ICT service supply chains"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_02_01.c0010,
        description="Contractual arrangement reference number",
    )
    c0020: str = Field(
        primary_key=True, max_length=255, description="Type of ICT services"
    )
    c0030: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_05_01.c0010,
        description="Identification code of the third-party service provider",
    )
    c0040: str | None = Field(
        default=None,
        max_length=255,
        description="Type of code of the third-party service provider",
    )
    c0050: int = Field(primary_key=True, description="Rank")
    c0060: str = Field(
        primary_key=True,
        max_length=255,
        description="Identification code of the recipient of sub-contracted ICT services",
    )
    c0070: str | None = Field(
        default=None,
        max_length=255,
        description="Type of code of the recipient of sub-contracted ICT services",
    )


class B_06_01(SQLModel, table=True):
    """B.06.01 — Functions identification"""

    __table_code__ = "B.06.01"
    __table_display_name__ = "Functions identification"

    c0010: str = Field(
        primary_key=True, max_length=255, description="Function identifier"
    )
    c0020: str = Field(max_length=255, description="Licenced activity")
    c0030: str = Field(max_length=255, description="Function name")
    c0040: str = Field(
        primary_key=True,
        min_length=20,
        max_length=20,
        foreign_key=B_01_02.c0010,
        description="LEI of the financial entity",
    )
    c0050: str = Field(
        max_length=255, description="Criticality or importance assessment"
    )
    c0060: str = Field(
        max_length=255, description="Reasons for criticality or importance"
    )
    c0070: date = Field(
        description="Date of the last assessment of criticality or importance"
    )
    c0080: int = Field(description="Recovery time objective of the function")
    c0090: int = Field(description="Recovery point objective of the function")
    c0100: str = Field(
        max_length=255, description="Impact of discontinuing the function"
    )


class B_07_01(SQLModel, table=True):
    """B.07.01 — Assessment of the ICT services"""

    __table_code__ = "B.07.01"
    __table_display_name__ = "Assessment of the ICT services"

    c0010: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_02_01.c0010,
        description="Contractual arrangement reference number",
    )
    c0020: str = Field(
        primary_key=True,
        max_length=255,
        foreign_key=B_05_01.c0010,
        description="Identification code of the third-party service provider",
    )
    c0030: str = Field(
        max_length=255, description="Type of code of the third-party service provider"
    )
    c0040: str = Field(
        primary_key=True, max_length=255, description="Type of ICT services"
    )
    c0050: str = Field(
        max_length=255,
        description="Substitutability of the ICT third-party service provider",
    )
    c0060: str | None = Field(
        default=None,
        max_length=255,
        description="Reason if the ICT third-party service provider is considered not substitutable or difficult to be substitutable",
    )
    c0070: date = Field(
        description="Date of the last audit on the ICT third-party service provider"
    )
    c0080: bool = Field(description="Existence of an exit plan")
    c0090: str = Field(
        max_length=255,
        description="Possibility of reintegration of the contracted ICT service",
    )
    c0100: str = Field(
        max_length=255, description="Impact of discontinuing the ICT services"
    )
    c0110: bool = Field(
        description="Are there alternative ICT third-party service providers identified?"
    )
    c0120: str | None = Field(
        default=None,
        max_length=255,
        description="Identification of alternative ICT TPP",
    )


# Reference table for ICT Service Types (if needed as separate table)
class B_08_01(SQLModel, table=True):
    """Type of ICT Services reference table"""

    __table_code__ = "B.08.01"
    __table_display_name__ = "Type of ICT Services"

    identifier: str = Field(
        primary_key=True, max_length=50, description="Type of ICT services identifier"
    )
    name: str = Field(max_length=50, description="Type of ICT services name")
    description: str = Field(
        max_length=255, description="Type of ICT services description"
    )


class NamedModel(Protocol):
    __table_display_name__: str


# Utility function to get table display name
def get_table_display_name(model_class: NamedModel) -> str:
    """Get the display name for a table model"""
    return model_class.__table_display_name__


# Utility function to get column display name from description
def get_column_display_name(model_class: SQLModel, column_name: str) -> str:
    """Get the display name for a column from its description"""
    field = model_class.model_fields.get(column_name)
    if field and field.description:
        return field.description
    return column_name
