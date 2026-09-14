const CHUNKS=[{"t":"The Federal Reserve raised interest rates by 25 basis points.","g":"policy","k":13},{"t":"The Fed hiked rates a quarter point at its March meeting.","g":"policy","k":14},{"t":"The central bank increased borrowing costs to combat inflation.","g":"policy","k":12},{"t":"Policymakers lifted the benchmark rate to slow price growth.","g":"policy","k":12},{"t":"The dot plot signals two more hikes before year end.","g":"policy","k":13},{"t":"Nvidia beat consensus EPS estimates by eighteen percent.","g":"earnings","k":10},{"t":"Nvidia's quarterly earnings came in well above analyst forecasts.","g":"earnings","k":12},{"t":"Margins compressed as input costs outpaced pricing power.","g":"earnings","k":10},{"t":"Management guided full-year revenue below the street consensus.","g":"earnings","k":10},{"t":"Portfolio variance is dominated by the first three principal components.","g":"risk","k":13},{"t":"Most of the covariance matrix's energy sits in a handful of eigenvalues.","g":"risk","k":16},{"t":"We shrink the sample covariance toward a structured factor model.","g":"risk","k":13},{"t":"Marchenko-Pastur gives the noise threshold for sample eigenvalues.","g":"risk","k":10},{"t":"Sentence embeddings map text into a fixed-dimensional vector space.","g":"method","k":12},{"t":"Cosine similarity measures the angle between two embedding vectors.","g":"method","k":12},{"t":"Shannon entropy quantifies the average information content of a distribution.","g":"method","k":13},{"t":"Truncated SVD gives the optimal low-rank approximation of a matrix.","g":"method","k":13},{"t":"My dog refuses to eat anything except wild-caught salmon.","g":"unrelated","k":12},{"t":"The hiking trail was closed due to snowpack above the treeline.","g":"unrelated","k":14},{"t":"She repainted the kitchen cabinets a deep forest green.","g":"unrelated","k":12}];
const SIM=[
[1,0.544,0.456,0.391,0.264,0.226,0.201,0.253,0.212,0.075,0.03,0.156,0.002,0.098,0.039,-0.01,0.035,-0.061,0.058,0.02],
[0.544,1,0.375,0.43,0.445,0.138,0.189,0.191,0.231,-0.036,-0.107,0.087,-0.017,-0.003,-0.051,-0.09,-0.017,-0.031,0.156,0.008],
[0.456,0.375,1,0.363,0.16,0.164,0.211,0.352,0.163,0.038,-0.055,0.116,-0.06,0.011,-0.065,-0.104,-0.026,-0.094,0.032,-0.005],
[0.391,0.43,0.363,1,0.198,0.323,0.282,0.363,0.285,0.025,-0.043,0.163,0.027,0.078,-0.013,0.002,0.154,-0.02,0.056,-0.059],
[0.264,0.445,0.16,0.198,1,0.121,0.218,0.065,0.242,0.021,0.031,0.09,0.028,0.08,0.141,-0.039,0.01,-0.104,0.3,-0.076],
[0.226,0.138,0.164,0.323,0.121,1,0.621,0.251,0.234,0.112,0.131,0.141,0.144,0.039,-0,0.059,0.154,0.019,-0.009,0.038],
[0.201,0.189,0.211,0.282,0.218,0.621,1,0.203,0.289,0.145,0.096,0.047,0.054,0.073,0.02,0.054,0.107,0.056,-0.002,0.02],
[0.253,0.191,0.352,0.363,0.065,0.251,0.203,1,0.211,0.161,0.135,0.287,0.093,0.108,0.123,0.207,0.272,-0.071,-0.017,0.005],
[0.212,0.231,0.163,0.285,0.242,0.234,0.289,0.211,1,0.075,-0.039,0.083,-0.007,0.018,-0.208,0.031,0.067,0.018,0.093,0.014],
[0.075,-0.036,0.038,0.025,0.021,0.112,0.145,0.161,0.075,1,0.473,0.313,0.324,0.057,0.121,0.097,0.194,0.079,-0.09,0.114],
[0.03,-0.107,-0.055,-0.043,0.031,0.131,0.096,0.135,-0.039,0.473,1,0.298,0.482,0.05,0.221,0.123,0.302,0.079,-0.034,0.085],
[0.156,0.087,0.116,0.163,0.09,0.141,0.047,0.287,0.083,0.313,0.298,1,0.232,0.22,0.222,0.113,0.29,-0.007,-0.031,0.052],
[0.002,-0.017,-0.06,0.027,0.028,0.144,0.054,0.093,-0.007,0.324,0.482,0.232,1,-0.06,0.119,0.224,0.354,0.017,0,0.027],
[0.098,-0.003,0.011,0.078,0.08,0.039,0.073,0.108,0.018,0.057,0.05,0.22,-0.06,1,0.337,0.203,0.16,0.069,-0.024,-0.037],
[0.039,-0.051,-0.065,-0.013,0.141,-0,0.02,0.123,-0.208,0.121,0.221,0.222,0.119,0.337,1,0.164,0.253,0.023,-0.062,-0.053],
[-0.01,-0.09,-0.104,0.002,-0.039,0.059,0.054,0.207,0.031,0.097,0.123,0.113,0.224,0.203,0.164,1,0.082,-0.02,-0.032,-0.063],
[0.035,-0.017,-0.026,0.154,0.01,0.154,0.107,0.272,0.067,0.194,0.302,0.29,0.354,0.16,0.253,0.082,1,0.059,0.074,-0.046],
[-0.061,-0.031,-0.094,-0.02,-0.104,0.019,0.056,-0.071,0.018,0.079,0.079,-0.007,0.017,0.069,0.023,-0.02,0.059,1,0.026,0.046],
[0.058,0.156,0.032,0.056,0.3,-0.009,-0.002,-0.017,0.093,-0.09,-0.034,-0.031,0,-0.024,-0.062,-0.032,0.074,0.026,1,0.005],
[0.02,0.008,-0.005,-0.059,-0.076,0.038,0.02,0.005,0.014,0.114,0.085,0.052,0.027,-0.037,-0.053,-0.063,-0.046,0.046,0.005,1]
];
