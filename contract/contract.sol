// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/// @title Simple ERC20 for testing
contract TestStableCoin {
    string public name = "TestUSD";
    string public symbol = "TUSD";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor(uint256 _initialSupply) {
        _mint(msg.sender, _initialSupply);
    }

    function _mint(address to, uint256 amount) internal {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "Insufficient balance");
        require(allowance[from][msg.sender] >= amount, "Allowance exceeded");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}

/// @title Carbon Credit Token
contract CarbonCreditToken {
    string public name = "BlueCarbon";
    string public symbol = "BCARB";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    TestStableCoin public stablecoin;

    mapping(address => uint256) public balanceOf;

    // Roles
    mapping(address => bool) public isAdmin;
    mapping(address => bool) public isVerifier;
    mapping(address => bool) public isManager;

    struct Project {
        address owner;
        address beneficiary;
        uint32[4] payoutBps; // [community, ngo, verifier, remainder]
        uint256 escrow;
        uint256 totalIssued;
        uint256 totalRetired;
        bool exists;
    }

    mapping(uint256 => Project) public projects;

    // Events
    event CreditsIssued(uint256 indexed projectId, address indexed to, uint256 tonnes);
    event VerificationFulfilled(uint256 indexed projectId, uint256 tonnes, uint256 pricePerTonne);
    event PayoutDistributed(uint256 indexed projectId, uint256 amount);
    event CreditsRetired(address indexed who, uint256 amount, uint256 timestamp);
    event ProjectCreated(uint256 indexed projectId, address indexed owner, address beneficiary, uint32[4] payoutBps);

    constructor(address _stablecoin) {
        stablecoin = TestStableCoin(_stablecoin);
        isAdmin[msg.sender] = true;
    }

    modifier onlyAdmin() {
        require(isAdmin[msg.sender], "Not admin");
        _;
    }

    modifier onlyManager() {
        require(isManager[msg.sender], "Not manager");
        _;
    }

    modifier onlyVerifier() {
        require(isVerifier[msg.sender], "Not verifier");
        _;
    }

    // Role management
    function grantManager(address account) external onlyAdmin {
        isManager[account] = true;
    }

    function grantVerifier(address account) external onlyAdmin {
        isVerifier[account] = true;
    }

    function grantAdmin(address account) external onlyAdmin {
        isAdmin[account] = true;
    }

    // Mint function internal
    function _mint(address to, uint256 amount) internal {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    // Burn function internal
    function _burn(address from, uint256 amount) internal {
        require(balanceOf[from] >= amount, "Insufficient balance");
        balanceOf[from] -= amount;
        totalSupply -= amount;
    }

    // Create project
    function createProject(
        uint256 projectId,
        address owner,
        address beneficiary,
        uint32[4] calldata payoutBps
    ) external onlyManager {
        require(!projects[projectId].exists, "Project exists");
        projects[projectId] = Project({
            owner: owner,
            beneficiary: beneficiary,
            payoutBps: payoutBps,
            escrow: 0,
            totalIssued: 0,
            totalRetired: 0,
            exists: true
        });
        emit ProjectCreated(projectId, owner, beneficiary, payoutBps);
    }

    // Deposit escrow
    function depositEscrow(uint256 projectId, uint256 amount) external {
        require(projects[projectId].exists, "Project does not exist");
        require(stablecoin.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        projects[projectId].escrow += amount;
    }

    // Fulfill verification
    function fulfillVerification(uint256 projectId, uint256 tonnes, uint256 pricePerTonne) external onlyVerifier {
        Project storage p = projects[projectId];
        require(p.exists, "Project does not exist");

        _mint(p.owner, tonnes);
        p.totalIssued += tonnes;

        emit CreditsIssued(projectId, p.owner, tonnes);
        emit VerificationFulfilled(projectId, tonnes, pricePerTonne);

        uint256 totalPayout = tonnes * pricePerTonne;
        if (p.escrow >= totalPayout) {
            p.escrow -= totalPayout;
            _distributePayouts(projectId, totalPayout);
        }
    }

    function _distributePayouts(uint256 projectId, uint256 amount) internal {
        Project storage p = projects[projectId];

        uint256 communityShare = (amount * p.payoutBps[0]) / 10000;
        uint256 ngoShare       = (amount * p.payoutBps[1]) / 10000;
        uint256 verifierShare  = (amount * p.payoutBps[2]) / 10000;
        uint256 platformShare  = amount - (communityShare + ngoShare + verifierShare);

        if (communityShare > 0) stablecoin.transfer(p.beneficiary, communityShare);
        if (ngoShare > 0) stablecoin.transfer(p.owner, ngoShare);
        if (verifierShare > 0) stablecoin.transfer(msg.sender, verifierShare);

        // Send remainder to first admin
        address platformAdmin = msg.sender; // fallback
        for(uint i=0;i<1;i++){ // first admin is msg.sender in this simplified version
            if(isAdmin[msg.sender]) platformAdmin = msg.sender;
        }
        if(platformShare > 0) stablecoin.transfer(platformAdmin, platformShare);

        emit PayoutDistributed(projectId, amount);
    }

    // Retire credits
    function retire(uint256 amount) external {
        _burn(msg.sender, amount);
        emit CreditsRetired(msg.sender, amount, block.timestamp);
    }
}
