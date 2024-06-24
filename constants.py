import re
import csv


overlapping_extensions = {
    'rv_zcmt': {'rv_c_d'},
    'rv_zcmp': {'rv_c_d'},
    'rv_c': {'rv_zcmop'},
}

overlapping_instructions = {
    'c_addi': {'c_nop'},
    'c_lui': {'c_addi16sp'},
    'c_mv': {'c_jr'},
    'c_jalr': {'c_ebreak'},
    'c_add': {'c_ebreak', 'c_jalr'},
}

isa_regex = \
re.compile("^RV(32|64|128)[IE]+[ABCDEFGHJKLMNPQSTUVX]*(Zicsr|Zifencei|Zihintpause|Zam|Ztso|Zkne|Zknd|Zknh|Zkse|Zksh|Zkg|Zkb|Zkr|Zks|Zkn|Zba|Zbc|Zbb|Zbp|Zbr|Zbm|Zbs|Zbe|Zbf|Zbt|Zmmul|Zbpbo|Zca|Zcf|Zcd|Zcb|Zcmp|Zcmt){,1}(_Zicsr){,1}(_Zifencei){,1}(_Zihintpause){,1}(_Zmmul){,1}(_Zam){,1}(_Zba){,1}(_Zbb){,1}(_Zbc){,1}(_Zbe){,1}(_Zbf){,1}(_Zbm){,1}(_Zbp){,1}(_Zbpbo){,1}(_Zbr){,1}(_Zbs){,1}(_Zbt){,1}(_Zkb){,1}(_Zkg){,1}(_Zkr){,1}(_Zks){,1}(_Zkn){,1}(_Zknd){,1}(_Zkne){,1}(_Zknh){,1}(_Zkse){,1}(_Zksh){,1}(_Ztso){,1}(_Zca){,1}(_Zcf){,1}(_Zcd){,1}(_Zcb){,1}(_Zcmp){,1}(_Zcmt){,1}$")

# regex to find <msb>..<lsb>=<val> patterns in instruction
fixed_ranges = re.compile(
    '\s*(?P<msb>\d+.?)\.\.(?P<lsb>\d+.?)\s*=\s*(?P<val>\d[\w]*)[\s$]*', re.M)

# regex to find <lsb>=<val> patterns in instructions
#single_fixed = re.compile('\s+(?P<lsb>\d+)=(?P<value>[\w\d]*)[\s$]*', re.M)
single_fixed = re.compile('(?:^|[\s])(?P<lsb>\d+)=(?P<value>[\w]*)((?=\s|$))', re.M)

# regex to find the overloading condition variable
var_regex = re.compile('(?P<var>[a-zA-Z][\w\d]*)\s*=\s*.*?[\s$]*', re.M)

# regex for pseudo op instructions returns the dependent filename, dependent
# instruction, the pseudo op name and the encoding string
pseudo_regex = re.compile(
    '^\$pseudo_op\s+(?P<filename>rv[\d]*_[\w].*)::\s*(?P<orig_inst>.*?)\s+(?P<pseudo_inst>.*?)\s+(?P<overload>.*)$'
, re.M)

imported_regex = re.compile('^\s*\$import\s*(?P<extension>.*)\s*::\s*(?P<instruction>.*)', re.M)

causes = []
with open("causes.csv") as f:
    csv_reader = csv.reader(f, skipinitialspace=True)
    for row in csv_reader:
        causes.append((int(row[0], 0), row[1]))
csrs = []
with open("csrs.csv") as f:
    csv_reader = csv.reader(f, skipinitialspace=True)
    for row in csv_reader:
        csrs.append((int(row[0], 0), row[1]))
csrs32 = []
with open("csrs32.csv") as f:
    csv_reader = csv.reader(f, skipinitialspace=True)
    for row in csv_reader:
        csrs32.append((int(row[0], 0), row[1]))
arg_lut = {}
with open("arg_lut.csv") as f:
    csv_reader = csv.reader(f, skipinitialspace=True)
    for row in csv_reader:
        k = row[0]
        v = (int(row[1]), int(row[2]))
        arg_lut[k] = v

# for mop
arg_lut['mop_r_t_30'] = (30,30)
arg_lut['mop_r_t_27_26'] = (27,26)
arg_lut['mop_r_t_21_20'] = (21, 20)
arg_lut['mop_rr_t_30'] = (30,30)
arg_lut['mop_rr_t_27_26'] = (27, 26)
arg_lut['c_mop_t'] = (10,8)

# dictionary containing the mapping of the argument to the what the fields in
# the latex table should be
latex_mapping = {}
latex_mapping['imm12'] = 'imm[11:0]'
latex_mapping['rs1'] = 'rs1'
latex_mapping['rs2'] = 'rs2'
latex_mapping['rd'] = 'rd'
latex_mapping['imm20'] = 'imm[31:12]'
latex_mapping['bimm12hi'] = 'imm[12$\\vert$10:5]'
latex_mapping['bimm12lo'] = 'imm[4:1$\\vert$11]'
latex_mapping['imm12hi'] = 'imm[11:5]'
latex_mapping['imm12lo'] = 'imm[4:0]'
latex_mapping['jimm20'] = 'imm[20$\\vert$10:1$\\vert$11$\\vert$19:12]'
latex_mapping['zimm'] = 'uimm'
latex_mapping['shamtw'] = 'shamt'
latex_mapping['shamtd'] = 'shamt'
latex_mapping['shamtq'] = 'shamt'
latex_mapping['rd_p'] = "rd\\,$'$"
latex_mapping['rs1_p'] = "rs1\\,$'$"
latex_mapping['rs2_p'] = "rs2\\,$'$"
latex_mapping['rd_rs1_n0'] = 'rd/rs$\\neq$0'
latex_mapping['rd_rs1_p'] = "rs1\\,$'$/rs2\\,$'$"
latex_mapping['c_rs2'] = 'rs2'
latex_mapping['c_rs2_n0'] = 'rs2$\\neq$0'
latex_mapping['rd_n0'] = 'rd$\\neq$0'
latex_mapping['rs1_n0'] = 'rs1$\\neq$0'
latex_mapping['c_rs1_n0'] = 'rs1$\\neq$0'
latex_mapping['rd_rs1'] = 'rd/rs1'
latex_mapping['zimm6hi'] = 'uimm[5]'
latex_mapping['zimm6lo'] = 'uimm[4:0]'
latex_mapping['c_nzuimm10'] = "nzuimm[5:4$\\vert$9:6$\\vert$2$\\vert$3]"
latex_mapping['c_uimm7lo'] = 'uimm[2$\\vert$6]'
latex_mapping['c_uimm7hi'] = 'uimm[5:3]'
latex_mapping['c_uimm8lo'] = 'uimm[7:6]'
latex_mapping['c_uimm8hi'] = 'uimm[5:3]'
latex_mapping['c_uimm9lo'] = 'uimm[7:6]'
latex_mapping['c_uimm9hi'] = 'uimm[5:4$\\vert$8]'
latex_mapping['c_nzimm6lo'] = 'nzimm[4:0]'
latex_mapping['c_nzimm6hi'] = 'nzimm[5]'
latex_mapping['c_imm6lo'] = 'imm[4:0]'
latex_mapping['c_imm6hi'] = 'imm[5]'
latex_mapping['c_nzimm10hi'] = 'nzimm[9]'
latex_mapping['c_nzimm10lo'] = 'nzimm[4$\\vert$6$\\vert$8:7$\\vert$5]'
latex_mapping['c_nzimm18hi'] = 'nzimm[17]'
latex_mapping['c_nzimm18lo'] = 'nzimm[16:12]'
latex_mapping['c_imm12'] = 'imm[11$\\vert$4$\\vert$9:8$\\vert$10$\\vert$6$\\vert$7$\\vert$3:1$\\vert$5]'
latex_mapping['c_bimm9lo'] = 'imm[7:6$\\vert$2:1$\\vert$5]'
latex_mapping['c_bimm9hi'] = 'imm[8$\\vert$4:3]'
latex_mapping['c_nzuimm5'] = 'nzuimm[4:0]'
latex_mapping['c_nzuimm6lo'] = 'nzuimm[4:0]'
latex_mapping['c_nzuimm6hi'] = 'nzuimm[5]'
latex_mapping['c_uimm8splo'] = 'uimm[4:2$\\vert$7:6]'
latex_mapping['c_uimm8sphi'] = 'uimm[5]'
latex_mapping['c_uimm8sp_s'] = 'uimm[5:2$\\vert$7:6]'
latex_mapping['c_uimm10splo'] = 'uimm[4$\\vert$9:6]'
latex_mapping['c_uimm10sphi'] = 'uimm[5]'
latex_mapping['c_uimm9splo'] = 'uimm[4:3$\\vert$8:6]'
latex_mapping['c_uimm9sphi'] = 'uimm[5]'
latex_mapping['c_uimm10sp_s'] = 'uimm[5:4$\\vert$9:6]'
latex_mapping['c_uimm9sp_s'] = 'uimm[5:3$\\vert$8:6]'

# created a dummy instruction-dictionary like dictionary for all the instruction
# types so that the same logic can be used to create their tables
latex_inst_type = {}
latex_inst_type['R-type'] = {}
latex_inst_type['R-type']['variable_fields'] = ['opcode', 'rd', 'funct3', \
        'rs1', 'rs2', 'funct7']
latex_inst_type['R4-type'] = {}
latex_inst_type['R4-type']['variable_fields'] = ['opcode', 'rd', 'funct3', \
        'rs1', 'rs2', 'funct2', 'rs3']
latex_inst_type['I-type'] = {}
latex_inst_type['I-type']['variable_fields'] = ['opcode', 'rd', 'funct3', \
        'rs1', 'imm12']
latex_inst_type['S-type'] = {}
latex_inst_type['S-type']['variable_fields'] = ['opcode', 'imm12lo', 'funct3', \
        'rs1', 'rs2', 'imm12hi']
latex_inst_type['B-type'] = {}
latex_inst_type['B-type']['variable_fields'] = ['opcode', 'bimm12lo', 'funct3', \
        'rs1', 'rs2', 'bimm12hi']
latex_inst_type['U-type'] = {}
latex_inst_type['U-type']['variable_fields'] = ['opcode', 'rd', 'imm20']
latex_inst_type['J-type'] = {}
latex_inst_type['J-type']['variable_fields'] = ['opcode', 'rd', 'jimm20']
latex_fixed_fields = []
latex_fixed_fields.append((31,25))
latex_fixed_fields.append((24,20))
latex_fixed_fields.append((19,15))
latex_fixed_fields.append((14,12))
latex_fixed_fields.append((11,7))
latex_fixed_fields.append((6,0))

# Pseudo-ops present in the generated encodings.
# By default pseudo-ops are not listed as they are considered aliases
# of their base instruction.
emitted_pseudo_ops = [
    'pause',
    'prefetch_i',
    'prefetch_r',
    'prefetch_w',
    'rstsa16',
    'rstsa32',
    'srli32_u',
    'slli_rv32',
    'srai_rv32',
    'srli_rv32',
    'umax32',
    'c_mop_1',
    'c_sspush_x1',
    'c_mop_3',
    'c_mop_5',
    'c_sspopchk_x5',
    'c_mop_7',
    'c_mop_9',
    'c_mop_11',
    'c_mop_13',
    'c_mop_15',
    'mop_r_0',
    'mop_r_1',
    'mop_r_2',
    'mop_r_3',
    'mop_r_4',
    'mop_r_5',
    'mop_r_6',
    'mop_r_7',
    'mop_r_8',
    'mop_r_9',
    'mop_r_10',
    'mop_r_11',
    'mop_r_12',
    'mop_r_13',
    'mop_r_14',
    'mop_r_15',
    'mop_r_16',
    'mop_r_17',
    'mop_r_18',
    'mop_r_19',
    'mop_r_20',
    'mop_r_21',
    'mop_r_22',
    'mop_r_23',
    'mop_r_24',
    'mop_r_25',
    'mop_r_26',
    'mop_r_27',
    'mop_r_28',
    'sspopchk_x1',
    'sspopchk_x5',
    'ssrdp',
    'mop_r_29',
    'mop_r_30',
    'mop_r_31',
    'mop_r_32',
    'mop_rr_0',
    'mop_rr_1',
    'mop_rr_2',
    'mop_rr_3',
    'mop_rr_4',
    'mop_rr_5',
    'mop_rr_6',
    'mop_rr_7',
    'sspush_x1',
    'sspush_x5',
    'lpad',
    'bclri.rv32',
    'bexti.rv32',
    'binvi.rv32',
    'bseti.rv32',
    'zext.h.rv32',
    'rev8.h.rv32',
    'rori.rv32',
]

COMPRESSED_SETS = [
    "C",
    "Zcf",
    "Zcd",
    "Zca",
    "Zce",
    "Zvb",
    "Zcmp",
    "Zcmt",
    "Zc"
]

SUPPORTED_EXTENSIONS = [
    "I",
    "A", 
    "B", 
    "C", 
    "D", 
    "F", 
    "E", 
    "M", 
    "Smaia", 
    "Smcdeleg", 
    "Smcsrind", 
    "Smepmp", 
    "Ssaia", 
    "Ssccfg",
    "Sscsrind",
    "Svpbmt",
    "V",
    "Za128rs",
    "Za64rs",
    "Zabha",
    "Zacas",
    "Zama16b",
    "Zba",
    "Zbb",
    "Zbc",
    "Zbkb",
    "Zbkc",
    "Zbkx",
    "Zbs",
    "Zca",
    "Zcb",
    "Zcd",
    "Zcf",
    "Zcmop",
    "Zcmp",
    "Zdinx",
    "Zfa",
    "Zfh",
    "Zfhmin",
    "Zfinx",
    "Zhinx",
    "Zhinxmin",
    "Zic64b",
    "Zicbop",
    "Ziccamoa",
    "Ziccif",
    "Zicclsm",
    "Ziccrse",
    "Zicntr",
    "Zicond",
    "Zicsr",
    "Zifencei",
    "Zihintntl",
    "Zihpm",
    "Zimop",
    "Zkn",
    "Zknd",
    "Zkne",
    "Zknh",
    "Zksed",
    "Zksh",
    "Zk",
    "Zkr",
    "Zks",
    "Zkt",
    "Zmmul",
    "Zve32x",
    "Zve32f",
    "Zve64x",
    "Zve64f",
    "Zve64d",
    "Zvfh",
    "Zvl32b",
    "Zvl64b",
    "Zvl128b",
    "Zvl256b",
    "Zvl512b",
    "Zvl1024b",
    "Zvl2048b",
    "Zvl4096b",
    "Zvl8192b",
    "Zvl16384b",
    "Zvl32768b",
    "Zvl65536b",
]

data_types = {
    "rd": ["Register_int", "Register_float"],
    "rt": [],
    "rs1": ["Register_int", "Register_float"],
    "rs2": ["Register_int", "Register_float"],
    "rs3": ["Register_int", "Register_float"],
    "aqrl": ["Mapping_ordering"],
    "aq": ["u8"],
    "rl": ["u8"],
    "fm": ["u8"],
    "pred": ["Mapping_fence"],
    "succ": ["Mapping_fence"],
    "rm": ["Mapping_round"],
    "funct3": ["u8"],
    "funct2": ["u8"],
    "imm20":  [],         
    "jimm20": [],         
    "imm12":  [],         
    "csr": ["Mapping_csr"],
    "imm12hi":  [],       
    "bimm12hi": [],       
    "imm12lo":  [],       
    "bimm12lo": [],       
    "shamtq": ["u8"],
    "shamtw": ["u8"],
    "shamtw4": ["u8"],
    "shamtd": ["u8"],
    "bs": ["u8"],
    "rnum": ["u8"],
    "rc": ["u8"], # ???
    "imm2": [],           
    "imm3": [],           
    "imm4": [],           
    "imm5": [],           
    "imm6": [],           
    "zimm": [],           
    "opcode": ["u8"],
    "funct7": ["u8"],
    "vd": ["Register_vec"],
    "vs3": ["Register_vec"],
    "vs1": ["Register_vec"],
    "vs2": ["Register_vec"],
    "vm": ["Mapping_vm"],
    "wd": ["u8"],
    "amoop": ["u8"],
    "nf": ["Mapping_seg"],
    "simm5": [],          
    "zimm5": [],          
    "zimm10": ["Mapping_vtypei"],
    "zimm11": ["Mapping_vtypei"],    
    "zimm6hi": [],        
    "zimm6lo": [],        
    "c_nzuimm10": [],     
    "c_uimm7lo": [],      
    "c_uimm7hi": [],      
    "c_uimm8lo": [],      
    "c_uimm8hi": [],      
    "c_uimm9lo": [],      
    "c_uimm9hi": [],      
    "c_nzimm6lo": [],     
    "c_nzimm6hi": [],     
    "c_imm6lo": [],       
    "c_imm6hi": [],       
    "c_nzimm10hi": [],    
    "c_nzimm10lo": [],    
    "c_nzimm18hi": [],    
    "c_nzimm18lo": [],    
    "c_imm12": [],        
    "c_bimm9lo": [],      
    "c_bimm9hi": [],      
    "c_nzuimm5": [],      
    "c_nzuimm6lo": [],    
    "c_nzuimm6hi": [],    
    "c_uimm8splo": [],    
    "c_uimm8sphi": [],    
    "c_uimm8sp_s": [],    
    "c_uimm10splo": [],   
    "c_uimm10sphi": [],   
    "c_uimm9splo": [],    
    "c_uimm9sphi": [],    
    "c_uimm10sp_s": [],   
    "c_uimm9sp_s": [],    
    "c_uimm2": [],        
    "c_uimm1": [],        
    "c_rlist": [],        # TODO extra special handling
    "c_spimm": [],        # TODO extra special handling
    "c_index": [],        
    "rs1_p": ["Register_int_c", "Register_float_c"],    
    "rs2_p": ["Register_int_c", "Register_float_c"],
    "rd_p": ["Register_int_c", "Register_float_c"],
    "rd_rs1_n0": ["Register_int", "Register_float"],
    "rd_rs1_p": ["Register_int_c", "Register_float_c"],
    "rd_rs1": ["Register_int", "Register_float"],
    "rd_n2": ["Register_int", "Register_float"],            
    "rd_n0": ["Register_int", "Register_float"],            
    "rs1_n0": ["Register_int", "Register_float"],           
    "c_rs2_n0": ["Register_int", "Register_float"],         
    "c_rs1_n0": ["Register_int", "Register_float"],         
    "c_rs2": ["Register_int", "Register_float"],
    "c_sreg1": ["Register_int_c", "Register_float_c"],
    "c_sreg2": ["Register_int_c", "Register_float_c"],
    "mop_r_t_30": [],
    "mop_r_t_27_26": [],
    "mop_r_t_21_20": [],
    "mop_rr_t_30": [],
    "mop_rr_t_27_26": [],
}

special_tests = {
    "rd_rs1_n0": [1, 2],
    "rd_n2": [1, 3],
    "c_nzimm6lo": [0, 0],
    "c_nzimm6hi": [0, 0],
    "rd_n0": [1, 2],
    "rs1_n0": [1, 2],
    "c_rs2_n0": [1, 2],
    "c_rs1_n0": [1, 2],
    "aqrl": [1, 2],
    "csr": [1, 2],
    "nf": [1, 2],
    "vd": [1, 0],
    "vs3": [1, 0],
    "vs1": [1, 0],
    "vs2": [1, 0],
}

unsigned_list = [
    "imm20",
    "zimm",
    "zimm5",
    "zimm6hi",
    "zimm6lo",
    "c_nzuimm10",
    "c_uimm7lo",
    "c_uimm7hi",
    "mop_r_t_30",
    "mop_r_t_27_26",
    "mop_r_t_21_20",
    "mop_rr_t_30",
    "mop_rr_t_27_26",
]

imm_mappings = {
    "imm20":  [[31, 12]],         
    "jimm20": [[20, 20], [10, 1], [11, 11], [19, 12]],         
    "imm12":  [[11, 0]],
    "imm12hi":  [[11, 5]],
    "bimm12hi": [[12, 12], [10, 5]],
    "imm12lo":  [[4, 0]],
    "bimm12lo": [[4, 1], [11, 11]],
    "imm2": [[1, 0]],   # unused
    "imm3": [[2, 0]],   # unused
    "imm4": [[3, 0]],   # unused
    "imm5": [[4, 0]],   # unused
    "imm6": [[5, 0]],   # unused
    "zimm": [[4, 0]],   
    "simm5": [[4, 0]],  
    "zimm5": [[4, 0]],  # Care, since values are mapped in processor: TODO check for how disassembly works
    "zimm6hi": [[5, 5]],
    "zimm6lo": [[4, 0]],        
    "c_nzuimm10": [[5, 4], [9, 6], [2, 2], [3, 3]], # TODO zero illegal
    "c_uimm7lo": [[2, 2], [6, 6]],      
    "c_uimm7hi": [[5, 3]],      
    "c_uimm8lo": [[7, 6]],      
    "c_uimm8hi": [[5, 3]],      
    "c_uimm9lo": [[7, 6]],                  # unused
    "c_uimm9hi": [[5, 5], [4, 4], [8, 8]],  # unused
    "c_nzimm6lo": [[4, 0]], 
    "c_nzimm6hi": [[5, 5]], 
    "c_imm6lo": [[4, 0]],       
    "c_imm6hi": [[5, 5]],       
    "c_nzimm10hi": [[9, 9]],    
    "c_nzimm10lo": [[4, 4], [6, 6], [8, 7], [5, 5]],    
    "c_nzimm18hi": [[17, 17]],    
    "c_nzimm18lo": [[16, 12]],    
    "c_imm12": [[11, 11], [4, 4], [9, 8], [10, 10], [6, 6], [7, 7], [3, 1], [5, 5]],        
    "c_bimm9lo": [[7, 6], [2, 1], [5, 5]],      
    "c_bimm9hi": [[8, 8], [4, 3]],      
    "c_nzuimm5": [],      # unused
    "c_nzuimm6lo": [[4, 0]],    
    "c_nzuimm6hi": [[5, 5]],    
    "c_uimm8splo": [[4, 2], [7, 6]],    
    "c_uimm8sphi": [[5, 5]],    
    "c_uimm8sp_s": [[5, 2], [7, 6]],    
    "c_uimm10splo": [],   # unused
    "c_uimm10sphi": [],   # unused
    "c_uimm9splo": [[4, 3], [8, 6]],    
    "c_uimm9sphi": [[5, 5]],    
    "c_uimm10sp_s": [],   # unused
    "c_uimm9sp_s": [[5, 3], [8, 6]],    
    "c_uimm2": [[0, 0], [1, 1]],        
    "c_uimm1": [[1, 1]],    # TODO special case        
    "c_spimm": [[5, 4]],    # TODO special case        
    "c_index": [[7, 0]],    # TODO must be >= 32        
    "mop_r_t_30": [[4, 4]],
    "mop_r_t_27_26": [[3, 2]],
    "mop_r_t_21_20": [[1, 0]],
    "mop_rr_t_30": [[2, 2]],
    "mop_rr_t_27_26": [[1, 0]],
}

Register_int = [
    "zero",
    "ra",
    "sp",
    "gp",
    "tp",
    "t0",
    "t1",
    "t2",
    "s0",
    "s1",
    "a0",
    "a1",
    "a2",
    "a3",
    "a4",
    "a5",
    "a6",
    "a7",
    "s2",
    "s3",
    "s4",
    "s5",
    "s6",
    "s7",
    "s8",
    "s9",
    "s10",
    "s11",
    "t3",
    "t4",
    "t5",
    "t6",
]
Register_int_c = [
    "s0",
    "s1",
    "a0",
    "a1",
    "a2",
    "a3",
    "a4",
    "a5",
]
Register_float = [
    "ft0",
    "ft1",
    "ft2",
    "ft3",
    "ft4",
    "ft5",
    "ft6",
    "ft7",
    "fs0",
    "fs1",
    "fa0",
    "fa1",
    "fa2",
    "fa3",
    "fa4",
    "fa5",
    "fa6",
    "fa7",
    "fs2",
    "fs3",
    "fs4",
    "fs5",
    "fs6",
    "fs7",
    "fs8",
    "fs9",
    "fs10",
    "fs11",
    "ft8",
    "ft9",
    "ft10",
    "ft11",
]
Register_float_c = [
    "fs0",
    "fs1",
    "fa0",
    "fa1",
    "fa2",
    "fa3",
    "fa4",
    "fa5",
]
Register_vec = [
    "v0",
    "v1",
    "v2",
    "v3",
    "v4",
    "v5",
    "v6",
    "v7",
    "v8",
    "v9",
    "v10",
    "v11",
    "v12",
    "v13",
    "v14",
    "v15",
    "v16",
    "v17",
    "v18",
    "v19",
    "v20",
    "v21",
    "v22",
    "v23",
    "v24",
    "v25",
    "v26",
    "v27",
    "v28",
    "v29",
    "v30",
    "v31",
]

Mapping_vm = [
    ", v0.t",
    "",
]

Mapping_fence = [
    "unknown",
    "w",
    "r",
    "rw",
    "o",
    "ow",
    "or",
    "orw",
    "i",
    "iw",
    "ir",
    "irw",
    "io",
    "iow",
    "ior",
    "iorw",
]

Mapping_round = [
    "rne",
    "rtz",
    "rdn",
    "rup",
    "rmm",
    "unknown",
    "unknown",
    "dyn",
]
Mapping_ordering = ["", ".rl", ".aq", ".aqrl"]


Mapping_vtypei = {
hex(0): "e8, m1, tu, mu",
hex(1): "e8, m2, tu, mu",
hex(2): "e8, m4, tu, mu",
hex(3): "e8, m8, tu, mu",
hex(5): "e8, mf8, tu, mu",
hex(6): "e8, mf4, tu, mu",
hex(7): "e8, mf2, tu, mu",
hex(8): "e16, m1, tu, mu",
hex(9): "e16, m2, tu, mu",
hex(10): "e16, m4, tu, mu",
hex(11): "e16, m8, tu, mu",
hex(13): "e16, mf8, tu, mu",
hex(14): "e16, mf4, tu, mu",
hex(15): "e16, mf2, tu, mu",
hex(16): "e32, m1, tu, mu",
hex(17): "e32, m2, tu, mu",
hex(18): "e32, m4, tu, mu",
hex(19): "e32, m8, tu, mu",
hex(21): "e32, mf8, tu, mu",
hex(22): "e32, mf4, tu, mu",
hex(23): "e32, mf2, tu, mu",
hex(24): "e64, m1, tu, mu",
hex(25): "e64, m2, tu, mu",
hex(26): "e64, m4, tu, mu",
hex(27): "e64, m8, tu, mu",
hex(29): "e64, mf8, tu, mu",
hex(30): "e64, mf4, tu, mu",
hex(31): "e64, mf2, tu, mu",
hex(64): "e8, m1, ta, mu",
hex(65): "e8, m2, ta, mu",
hex(66): "e8, m4, ta, mu",
hex(67): "e8, m8, ta, mu",
hex(69): "e8, mf8, ta, mu",
hex(70): "e8, mf4, ta, mu",
hex(71): "e8, mf2, ta, mu",
hex(72): "e16, m1, ta, mu",
hex(73): "e16, m2, ta, mu",
hex(74): "e16, m4, ta, mu",
hex(75): "e16, m8, ta, mu",
hex(77): "e16, mf8, ta, mu",
hex(78): "e16, mf4, ta, mu",
hex(79): "e16, mf2, ta, mu",
hex(80): "e32, m1, ta, mu",
hex(81): "e32, m2, ta, mu",
hex(82): "e32, m4, ta, mu",
hex(83): "e32, m8, ta, mu",
hex(85): "e32, mf8, ta, mu",
hex(86): "e32, mf4, ta, mu",
hex(87): "e32, mf2, ta, mu",
hex(88): "e64, m1, ta, mu",
hex(89): "e64, m2, ta, mu",
hex(90): "e64, m4, ta, mu",
hex(91): "e64, m8, ta, mu",
hex(93): "e64, mf8, ta, mu",
hex(94): "e64, mf4, ta, mu",
hex(95): "e64, mf2, ta, mu",
hex(128): "e8, m1, tu, ma",
hex(129): "e8, m2, tu, ma",
hex(130): "e8, m4, tu, ma",
hex(131): "e8, m8, tu, ma",
hex(133): "e8, mf8, tu, ma",
hex(134): "e8, mf4, tu, ma",
hex(135): "e8, mf2, tu, ma",
hex(136): "e16, m1, tu, ma",
hex(137): "e16, m2, tu, ma",
hex(138): "e16, m4, tu, ma",
hex(139): "e16, m8, tu, ma",
hex(141): "e16, mf8, tu, ma",
hex(142): "e16, mf4, tu, ma",
hex(143): "e16, mf2, tu, ma",
hex(144): "e32, m1, tu, ma",
hex(145): "e32, m2, tu, ma",
hex(146): "e32, m4, tu, ma",
hex(147): "e32, m8, tu, ma",
hex(149): "e32, mf8, tu, ma",
hex(150): "e32, mf4, tu, ma",
hex(151): "e32, mf2, tu, ma",
hex(152): "e64, m1, tu, ma",
hex(153): "e64, m2, tu, ma",
hex(154): "e64, m4, tu, ma",
hex(155): "e64, m8, tu, ma",
hex(157): "e64, mf8, tu, ma",
hex(158): "e64, mf4, tu, ma",
hex(159): "e64, mf2, tu, ma",
hex(192): "e8, m1, ta, ma",
hex(193): "e8, m2, ta, ma",
hex(194): "e8, m4, ta, ma",
hex(195): "e8, m8, ta, ma",
hex(197): "e8, mf8, ta, ma",
hex(198): "e8, mf4, ta, ma",
hex(199): "e8, mf2, ta, ma",
hex(200): "e16, m1, ta, ma",
hex(201): "e16, m2, ta, ma",
hex(202): "e16, m4, ta, ma",
hex(203): "e16, m8, ta, ma",
hex(205): "e16, mf8, ta, ma",
hex(206): "e16, mf4, ta, ma",
hex(207): "e16, mf2, ta, ma",
hex(208): "e32, m1, ta, ma",
hex(209): "e32, m2, ta, ma",
hex(210): "e32, m4, ta, ma",
hex(211): "e32, m8, ta, ma",
hex(213): "e32, mf8, ta, ma",
hex(214): "e32, mf4, ta, ma",
hex(215): "e32, mf2, ta, ma",
hex(216): "e64, m1, ta, ma",
hex(217): "e64, m2, ta, ma",
hex(218): "e64, m4, ta, ma",
hex(219): "e64, m8, ta, ma",
hex(221): "e64, mf8, ta, ma",
hex(222): "e64, mf4, ta, ma",
hex(223): "e64, mf2, ta, ma"
}

Mapping_csr = {}
for csr_val in csrs:
    Mapping_csr[hex(csr_val[0])] = csr_val[1]
for csr_val in csrs32:
    Mapping_csr[hex(csr_val[0])] = csr_val[1]

Mapping_seg = [
    "",
    "seg2",
    "seg3",
    "seg4",
    "seg5",
    "seg6",
    "seg7",
    "seg8",
]

Mappings = [
        {"name": "Register_int", "use": False, "pointer": Register_int},
        {"name": "Mapping_int_c", "use": False, "pointer": Register_int_c},
        {"name": "Register_float", "use": False, "pointer": Register_float},
        {"name": "Register_float_c", "use": False, "pointer": Register_float_c},
        {"name": "Register_vec", "use": False, "pointer": Register_vec},
        {"name": "Mapping_vm", "use": False, "pointer": Mapping_vm},
        {"name": "Mapping_fence", "use": False, "pointer": Mapping_fence},
        {"name": "Mapping_vtypei", "use": False, "pointer": Mapping_vtypei},
        {"name": "Mapping_round", "use": False, "pointer": Mapping_round},
        {"name": "Mapping_ordering", "use": False, "pointer": Mapping_ordering},
        {"name": "Mapping_csr", "use": False, "pointer": Mapping_csr},
        {"name": "Mapping_seg", "use": False, "pointer": Mapping_seg},
    ]